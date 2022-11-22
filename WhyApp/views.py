import datetime

from . import app, db
from flask import render_template, redirect, url_for, request, make_response
from .utils import check_client_net, instruction_text
from .models import Subject, Conjunctive, Disjunctive
import random, string, json, requests
import itertools
import numpy as np

# GLOBALS
cap_site_k = app.config["RECAPTCHA_SITE_KEY"]
cap_secret = app.config["RECAPTCHA_SECRET_KEY"]
exp_version = 'pure_conjunction'
p = [.2, .4, .6, .8, 1]
n_trials = 10


@app.route('/why', methods=["GET"])
def index():
    if check_client_net():  # if VPN
        m1 = "NETWORK ERROR!"
        m2 = "THIS STUDY MAY NOT BE COMPLETED USING A VPN, TOR NODE OR RELAY NETWORK. <br> " \
             "You must turn these off and refresh this page to continue."
        nxt = '/consent'
        return render_template('message.html', msg1=m1, msg2=m2, next=nxt)
    else:
        return redirect(url_for('real'), PROLIFIC_PID=request.args.get('PROLIFIC_PID'))


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

            new_subject = Subject(participant_id=pid, prolific_pid=request.get_json()['PROLIFIC_PID'],
                                  recaptcha_complete=True, study_version=exp_version)
            db.session.add(new_subject)
            db.session.commit()
            return redirect(url_for('consent', PID=pid, PROLIFIC_PID=request.get_json()['PROLIFIC_PID'], TRL=0))
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
        if ss.recaptcha_complete == True:
            ss.ip_addy = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            ss.consent = True
            ss.in_progress = True
            ss.start_time = datetime.datetime.now()
            ss.prolific_pid = sdat['prolific_id']
            db.session.add(ss)
            db.session.commit()
        else:
            return render_template('message.html', msg1="ERROR", msg2="YOU CANNOT ACCESS THIS", next='/real')

        return make_response("200")


@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
    if request.method == 'GET':
        title = "Instructions"
        next_pg = "/acheck"
        return render_template('instruct.html', title=title, stim=instruction_text[exp_version], next=next_pg)


@app.route('/nxt_trl', methods=["GET"])
def nxt_trl():
    if request.method == "GET":
        t = int(request.args.get('TRL'))+1

        #if int(request.args.get('TRL')) in check_trials:
         #   return redirect(url_for('trial_chk', PID=request.args.get("PID"), TRL=t))
        if t != n_trials+1:
            return redirect(url_for('trial', PID=request.args.get("PID"), TRL=t))
        else:
            return render_template('message.html', msg1="Thank You!", msg2="You have finished this portion of the "
                                                                           "experiment. Press the spacebar to continue",
                                   next='/debrief')


jars = {'A': 'c1', 'B': 'c2', 'C': 'c3'}


@app.route('/trial_chk', methods=['GET', 'POST'])
def trial_chk():
    if request.method == 'GET':
        last_t = Conjunctive.query.filter_by(trl_num=int(request.args.get('TRL')) , participant_id=request.args.get("PID")).first()

        jar = np.random.choice(list(jars.keys()))  # pick a random jar
        if getattr(last_t, 'p_'+jars[jar]) < 0.5:  # get the prob of random jar on last trial. check if less than .5
            correct_answer = 'blue'
        else:
            correct_answer = 'red'
        return render_template('trial_chk.html', correct=correct_answer, jar=jar)
    if request.method == 'POST':
        tdat = request.get_json()
        last_t = Conjunctive.query.filter_by(trl_num=tdat['trl'], participant_id=tdat['pid']).first()
        last_t.jar_checked= tdat['jar']
        last_t.check_correct = bool(int(tdat['correct']))
        db.session.add(last_t)
        db.session.commit()

        return make_response('200')

@app.route('/iti')
def iti():
    return render_template('ITI.html')


@app.route('/trial', methods=["GET", "POST"])
def trial():
    if request.method == "GET":
        pC = [list(itertools.product(p, p, p))[x] for x in np.random.choice(len(p) ** 3, size=1, replace=False)]
        return render_template('trial1.html', jars=['A', 'B', 'C'], p=[int(x*100) for x in pC[0]],
                               trl=int(request.args.get("TRL")), max_t=n_trials, tcheck=int(1))
    if request.method == "POST":
        tdat = request.get_json()
        if 'conjunction' in exp_version:
            trl = Conjunctive(p_c1=float(tdat['p_c1']/100), p_c2=float(tdat['p_c2']/100), p_c3=float(tdat['p_c3']/100),
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
        sdat = Subject.query.filter_by(participant_id=request.args.get("PID")).first()
        sdat.complete = True
        sdat.complete_time = datetime.datetime.now()
        sdat.in_progress = False
        db.session.add(sdat)
        db.session.commit()
        print('subject complete!')
        return render_template('debrief.html')


@app.route('/acheck', methods=['GET', 'POST'])
def acheck():
    if request.method == 'GET':
        return render_template('acheck.html')
    if request.method == 'POST':
        d = request.get_json()
        sdat = Subject.query.filter_by(participant_id=d['subject_id']).first()
        if sorted(d['q1']) == ['check2', 'check3', 'check5']:
            sdat.attn_chck = True
            sdat.attn_chck2 = d['q2']
            db.session.add(sdat)
            db.session.commit()
            #return redirect(url_for('begin'))
        else:
            sdat.attn_chck = False
            #return redirect(url_for('oops'))

        return make_response('200')


@app.route('/begin', methods=['GET', 'POST'])
def begin():
    return render_template('message.html', msg1="Great!",
                           msg2="Press the space bar to begin...",
                           next="/iti")


@app.route('/oops', methods=['GET', 'POST'])
def oops():
    return render_template('message.html', msg1="Oops!",
                           msg2="You've answered one of the comprehension questions incorrectly, hit the space bar to return to the instructions.",
                           next="/instructions")
