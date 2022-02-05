#!/usr/local/bin/python

import os
import argparse
import json
from flask import Flask, request, session, redirect, url_for, \
                  abort, render_template, flash, make_response, jsonify
from app import App, Web
from app.api import Transaction
from datetime import datetime

web = Web()
flsk = web.flsk


@flsk.teardown_appcontext
def close(error):
    pass

@flsk.route('/')
def index():
    """Default loaded webserver page index.html"""
    env = os.environ.get('HOSTNAME')
    #flash(f'Hostname {env}', category='success')

    if session.get('logged_in'):
        entries = [{"id":1, "title":"Choose your car", "text":"You will see if you need to pay"}]
    else:
        entries = [{"id":2, "title":"Container", "text":f"{env}"}]
    return render_template('index.html', entries=entries)

@flsk.route('/adyen_display', methods=['GET', 'POST'])
def adyen():
    """Process Adyen Display messages"""
    error = None
    web.logger.warn(f"{json.dumps(request.json)}")
    data = {'message': 'OK', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 200)

@flsk.route('/login', methods=['GET', 'POST'])
def login():
    """Create session when correct user/password provided"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            rsp = web.getAuthentication(username, password)
            if rsp:
                error = rsp
            else:
                session['logged_in'] = True
                flash('You were logged in', category='success')
                return redirect(url_for('index'))
        else:
            error = "Missing credentials"

    return render_template('login.html', error=error)

@flsk.route('/logout')
def logout():
    """Close session for logged user"""
    if not session.get('logged_in'):
        abort(401)
    session.pop('logged_in', None)
    flash('You were logged out', category='success')
    return redirect(url_for('index'))

@flsk.route('/trx', methods=['GET', 'POST'])
def trx():
    """Response from PGS about current transaction APPROVED/DECLINED and showing Receipt of transaction"""
    if not session.get('logged_in'):
        abort(401)
    trx = web.trxs[-1]
    trx.shoppingCartUuid = request.args.get('shoppingCartUuid', default = "", type = str)
    trx.mediaType = request.args.get('mediaType', default = "", type = str)
    trx.correlationId = request.args.get('correlationId', default = "", type = str)
    trx.trxId = request.args.get('payId', default = "", type = str)
    trx.maskedMediaId = request.args.get('maskedMediaId', default = "", type = str)
    trx.status = request.args.get('status', default = "", type = str)
    trx.author_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    web.logger.info(f"ShoppingCart {trx.shoppingCartUuid} Transaction {trx.trxId} {trx.mediaType} {trx.maskedMediaId} {trx.status}")
    return render_template('trx.html', trx=trx)

@flsk.route('/approved', methods=['GET', 'POST'])
def approved():
    """Response from PGS about current APPROVED transaction - successURL"""
    # if not session.get('logged_in'):
    #     abort(401)
    status = request.args.get('status', default = "", type = str)
    flash(f'Approved {status}', category='success')
    trx = web.trxs[-1]
    isTokenized = request.args.get('isTokenized', default = False, type = bool)
    if (isTokenized):
        web.logger.info(f"Transaction amount: {trx.amount} {trx.currency} Method: {trx.trx_methods[trx.trx_method_choosen]} APPROVED and tokenized")
        web.tokens.append(trx.pgsTokenUuid)
        flash(f'Tokenized {status}', category='success')
    else:
        web.logger.info(f"Transaction amount: {trx.amount} {trx.currency} Method: {trx.trx_methods[trx.trx_method_choosen]} APPROVED")
        if (trx.clientHandleUuid is not None):
            web.tokens.append(trx.pgsTokenUuid)
            flash(f'{trx.trx_methods[trx.trx_method_choosen]} tokenized', category='success')
    return redirect(url_for('trx', **request.args))

@flsk.route('/declined', methods=['GET', 'POST'])
def declined():
    """Response from PGS about current DECLINED transaction - failureURL"""
    # if not session.get('logged_in'):
    #     abort(401)
    status = request.args.get('status', default = "", type = str)
    flash(f'Declined {status}', category='error')
    trx = web.trxs[-1]
    isTokenized = request.args.get('isTokenized', default = False, type = bool)
    if (isTokenized):
        web.logger.info(f"Transaction amount: {trx.amount} {trx.currency} Method: {trx.trx_methods[trx.trx_method_choosen]} DECLINED and tokenized")
        web.tokens.append(trx.pgsTokenUuid)
        flash(f'{trx.trx_methods[trx.trx_method_choosen]} tokenized', category='success')
    else:
        web.logger.info(f"Transaction amount: {trx.amount} {trx.currency} Method: {trx.trx_methods[trx.trx_method_choosen]} DECLINED")
        if trx.action == "Pay & Tokenize":
            web.tokens.append(trx.pgsTokenUuid)
            if (trx.clientHandleUuid is not None):
                flash(f'{trx.trx_methods[trx.trx_method_choosen]} tokenized', category='success')
            else:
                flash(f'{trx.trx_methods[trx.trx_method_choosen]} not tokenized', category='error')
        elif trx.action == "Tokenize":
            flash(f'{trx.trx_methods[trx.trx_method_choosen]} not tokenized', category='error')

    return redirect(url_for('trx', **request.args))


@flsk.route('/trx_done', methods=['GET', 'POST'])
def trx_done():
    """Pressed 'Done' button after showing Receipt of transaction"""
    if not session.get('logged_in'):
        abort(401)
    if request.form['url'] == 'None':
        return redirect(url_for('index'))


@flsk.route('/pay', methods=['GET', 'POST'])
def pay():
    """Pay shopping cart with choosen payment method and redirect to PSP page"""
    if not session.get('logged_in'):
        abort(401)
    if request.form['method_id'] == 'None':
        return redirect(url_for('index'))
    else:
        trx = web.trxs[-1]
        trx.trx_method_choosen = int(request.form['method_id'])
        web.logger.info(f"Transaction amount {trx.amount} {trx.currency} Method {trx.trx_methods[trx.trx_method_choosen]} {trx.trx_urls[trx.trx_method_choosen]}")
        return redirect(trx.trx_urls[trx.trx_method_choosen])


@flsk.route('/cart', methods=['GET', 'POST'])
def cart():
    """Get/Show shopping cart and possible payment methods"""
    if not session.get('logged_in'):
        abort(401)

    if request.form['button'] == "Pay":
        trx = web.get_shoppingCart(request.form['pp'], request.form['lpn'], request.form['amount'], False)
    elif request.form['button'] == "Pay & Tokenize":
        trx = web.get_shoppingCart(request.form['pp'], request.form['lpn'], request.form['amount'], True)
    elif request.form['button'] == "Pay with Token":
        trx = web.get_tokenCart(request.form['pp'], request.form['lpn'], request.form['amount'])
    elif request.form['button'] == "Tokenize":
        trx = web.get_tokenize(request.form['pp'], request.form['lpn'], request.form['amount'])
    elif request.form['button'] == "Validate Token":
        if len(web.trxs):
            trx = web.get_tokenValidity(web.trxs[-1])
        else:
            flash(f'No token exist', category='error')
            return redirect(url_for('index'))
    elif request.form['button'] == "Delete Token":
        if len(web.trxs):
            trx = web.get_tokenDelete(web.trxs[-1])
        else:
            flash(f'No token exist', category='error')
            return redirect(url_for('index'))
    elif request.form['button'] == "Refund":
        if len(web.trxs):
            trx = web.do_refundCart(web.trxs[-1])
        else:
            flash(f'No shopping cart exist', category='error')
            return redirect(url_for('index'))

    trx.action = request.form['button']
    if trx.rsp_status_code == 200:
        #data = json.loads(trx.rsp_text)
        # if trx.shoppingCartUuid:
        #     flash(f'Shopping cart: {trx.shoppingCartUuid}', category='success')

        if request.form['button'] == "Pay":
            trx = web.get_pay_methods(trx)
        elif request.form['button'] == "Pay & Tokenize":
            trx = web.get_pay_methods(trx)
        elif request.form['button'] == "Pay with Token":
            if len(web.tokens):
                trx.pgsTokenUuid = web.tokens[-1]
                trx = web.pay_tokenCart(trx, "CUSTOMER")
                if trx.rsp_status_code == 200:
                    if trx.status == "SUCCESS":
                        flash(f'{trx.action} Approved {trx.status}', category='success')
                    else:
                        flash(f'{trx.action} Declined {trx.status}', category='error')

                    return render_template('trx.html', trx=trx)
            else:
                flash(f'{trx.action} No token available', category='error')
        elif request.form['button'] == "Tokenize":
            trx = web.get_token_methods(trx)
        elif request.form['button'] == "Validate Token":
            if trx.tokenStatus == "IDLE" or trx.tokenStatus == "PENDING" or trx.tokenStatus == "VALID":
                flash(f'{trx.action} {trx.pgsTokenUuid} - {trx.tokenStatus}', category='success')
                flash(f'Card: {trx.mediaType}', category='success')
                flash(f'PAN: {trx.maskedMediaId}', category='success')
                flash(f'Exp: {trx.mediaExpiry}', category='success')
            else:
                flash(f'{trx.action} {trx.pgsTokenUuid} - {trx.tokenStatus}', category='error')
                flash(f'Card: {trx.mediaType}', category='error')
                flash(f'PAN: {trx.maskedMediaId}', category='error')
                flash(f'Exp: {trx.mediaExpiry}', category='error')
            return redirect(url_for('index'))
        elif request.form['button'] == "Delete Token":
            flash(f'{trx.action} {trx.pgsTokenUuid} - {trx.tokenStatus}', category='success')
            flash(f'Msg: {trx.details}', category='success')
            return redirect(url_for('index'))
        elif request.form['button'] == "Refund":
            flash(f'{trx.action} Shopping cart: {trx.shoppingCartUuid} Refund - {trx.status}', category='success')
            flash(f'HTTP: {trx.rsp_status_code} {trx.rsp_text}', category='success')
            return redirect(url_for('index'))

        #data = json.loads(trx.rsp_text)
    # elif trx.rsp_status_code == 500:
    #     flash(f'Generate shopping cart failed - {trx.rsp_status_code} Internal server error', category='error')
    else:
        if request.form['button'] == "Refund":
            flash(f'{trx.action} Shopping cart: {trx.shoppingCartUuid} Refund - {trx.status}', category='error')
            flash(f'HTTP: {trx.rsp_status_code} {trx.rsp_text}', category='error')
            return redirect(url_for('index'))
        else:
            flash(f'{trx.action} Generate cart failed - {trx.rsp_status}', category='error')
            flash(f'HTTP: {trx.rsp_status_code} {trx.rsp_text}', category='error')

    return render_template('cart.html', len=len(trx.trx_methods), trx=trx)


# Car selection

@flsk.route('/ParkPlace_1')
def ParkPlace_1():
    """Customer choose car on Parking place 1"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"1", "lpn":"ZA 864KL", "amount":"250", "display_amount":"2,50"}
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_2')
def ParkPlace_2():
    """Customer choose car on Parking place 2"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"2", "lpn":"BL 235PP", "amount":"1400", "display_amount":"14,00"}
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_3')
def ParkPlace_3():
    """Customer choose car on Parking place 3"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"3", "lpn":"BY 698LT", "amount":"50", "display_amount":"0,50"}
    flash('You can leave in 10 minutes')
    return render_template('pay.html', customer=customer)
    # return redirect(url_for('index'))

@flsk.route('/ParkPlace_4')
def ParkPlace_4():
    """Customer choose car on Parking place 4"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"4", "lpn":"FREE", "amount":"100", "display_amount":"1,00"}
    flash('You can Reserve parking place for next 2 hour')
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_5')
def ParkPlace_5():
    """Customer choose car on Parking place 5"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"5", "lpn":"MG TW777", "amount":"840", "display_amount":"8,40"}
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_6')
def ParkPlace_6():
    """Customer choose car on Parking place 6"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"6", "lpn":"3 SAM 123", "amount":"4200", "display_amount":"42,00"}
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_7')
def ParkPlace_7():
    """Customer choose car on Parking place 7"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"7", "lpn":"FREE", "amount":"0", "display_amount":"0,00"}
    flash('You can Reserve parking place for next 1 hour')
    return render_template('pay.html', customer=customer)

@flsk.route('/ParkPlace_8')
def ParkPlace_8():
    """Customer choose car on Parking place 8"""
    if not session.get('logged_in'):
        abort(401)
    customer = {"id":"8", "lpn":"KY 68 WZM", "amount":"99980", "display_amount":"999,80"}
    return render_template('pay.html', customer=customer)



if __name__ == "__main__":
    __version_info__ = ('0','1','0')
    __version__ = '.'.join(__version_info__)

    parser = argparse.ArgumentParser(prog="POS",
                                        description='POS test terminals',
                                        epilog='Pavol Hudák')
    parser.add_argument('-v', '--version', action='version',
                                version='%(prog)s ('+__version__+')')
    parser.add_argument('-c', '--config', dest='config_file_path',
                                action='store',
                                default="./app/config.yml",
                                help='Path to config file (default: %(default)s)')
    parser.add_argument('-e', '--env', dest='inout_env',
                                action='store',
                                default="production",
                                help='Define execution environment (default: %(default)s)')
    parser.add_argument('-p', '--port', dest='web_port',
                                action='store',
                                default="80",
                                help='Define web server port (default: %(default)s)')

    app = App(__version__, parser.parse_args())
    app.run(web)
    app.finished()
    