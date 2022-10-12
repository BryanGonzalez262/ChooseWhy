import datetime

from . import app, db
from flask import render_template, redirect, url_for, request, make_response
from .utils import check_client_net
from .models import Subject, Conjunctive, Disjunctive
import random, string, json, requests
import itertools
import numpy as np

# GLOBALS
cap_site_k = app.config["RECAPTCHA_SITE_KEY"]
cap_secret = app.config["RECAPTCHA_SECRET_KEY"]
exp_version = '1_conjunction'
p = [.2, .4, .6, .8, 1]
n_trials = 3


@app.route('/', methods=["GET"])
def index():
    if check_client_net():  # if VPN
        m1 = "NETWORK ERROR!"
        m2 = "THIS STUDY MAY NOT BE COMPLETED USING A VPN, TOR NODE OR RELAY NETWORK. <br> " \
             "You must turn these off and refresh this page to continue."
        nxt = '/consent'
        return render_template('message.html', msg1=m1, msg2=m2, next=nxt)
    else:
        return redirect(url_for('real'))


@app.route('/real', methods=["GET", "POST"])
def real():
    if request.method == "GET":
        return render_template('real.html', msg1='Please verify', message=' ', nxt="/consent", sk=cap_site_k)
    if request.method == "POST":
        r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data={'secret': cap_secret, 'response': request.form['g-recaptcha-response']})
        google_response = json.loads(r.text)
        if google_response['success']:
            pid = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                          for _ in range(16))
            print(f'SUCCESS subject:  {pid}')
            new_subject = Subject(participant_id=pid,  recaptcha_complete=True, study_version=exp_version)
            db.session.add(new_subject)
            db.session.commit()
            return redirect(url_for('consent', PID=pid, TRL=0))
        else:
            return render_template('message.html', msg1="ERROR", msg2="YOU CANNOT ACCESS THIS", next='/real')


@app.route('/consent', methods=['GET', 'POST'])
def consent():
    if request.method == 'GET':
        return render_template('consent.html')
    if request.method == 'POST':
        sdat = request.get_json()
        ss = Subject.query.filter_by(participant_id=sdat['subject_id'], recaptcha_complete=True,
                                     study_version=exp_version).first()
        ss.ip_addy = "ZZ.ZZZ.Z.ZZZ"  # request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        ss.consent = True
        ss.in_progress = True
        ss.start_time = datetime.datetime.now()
        db.session.add(ss)
        db.session.commit()
        return make_response("200")


@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
    if request.method == 'GET':
        title = "Welcome"
        stym = [
            "In this study, you will be shown winning lottery outcomes and the conditions necessary for the win.",
            "In each case, the winning outcome occurs when a red ball is drawn from each of three jars, A, B & C.",
            "You will also be shown the chances of drawing a red ball from each individual jar.",
            "Your task is to use the sliders on the screen to indicate how much you think each jar was "
            "responsible for the final, winning, outcome.",
            "There are no right or wrong answers. Please just indicate how much you think each jar caused the outcome",
            "Click Next to begin"]
        next_pg = "/nxt_trl"
        return render_template('instruct.html', title=title, stim=stym, next=next_pg)


@app.route('/nxt_trl', methods=["GET"])
def nxt_trl():
    if request.method == "GET":
        t = int(request.args.get('TRL'))+1
        if t != n_trials+1:
            return redirect(url_for('trial', PID=request.args.get("PID"), TRL=t))
        else:
            return render_template('message.html', msg1="Thank You!", msg2="You have finished this portion of the "
                                                                           "experiment. Press the spacebar to continue",
                                   next='/acheck')


@app.route('/iti')
def iti():
    return render_template('ITI.html')


@app.route('/trial', methods=["GET", "POST"])
def trial():
    if request.method == "GET":
        pC = [list(itertools.product(p, p, p))[x] for x in np.random.choice(len(p) ** 3, size=1, replace=False)]
        return render_template('trial.html', jars=['A', 'B', 'C'], p=pC[0], trl=int(request.args.get("TRL"))*10, max_t=n_trials)
    if request.method == "POST":
        tdat = request.get_json()
        if 'conjunction' in exp_version:
            trl = Conjunctive(p_c1=float(tdat['p_c1']/10), p_c2=float(tdat['p_c2']/10), p_c3=float(tdat['p_c3']/10),
                              c1_cause_rating=str(tdat['q_1']),
                              c2_cause_rating=str(tdat['q_2']),
                              c3_cause_rating=str(tdat['q_3']),
                              trl_num=int(tdat['trial']),
                              participant_id=tdat['subject_id'])
            db.session.add(trl)
            db.session.commit()
        return make_response("200")

@app.route('/debrief', methods=['GET', 'POST'])
def debrief():
    if request.method == "GET":
        return render_template('debrief.html')


@app.route('/acheck', methods=['GET', 'POST'])
def acheck():
    if request.method == 'GET':
        return render_template('acheck.html')
    if request.method == 'POST':
        d = request.get_json()
        sdat = Subject.query.filter_by(participant_id=d['subject_id']).first()
        if d['q1'] == ['check2', 'check3', 'check5']:
            sdat.attn_chck = True
        else:
            sdat.attn_chck = False
        sdat.attn_chck2 = d['q2']
        return make_response('200')