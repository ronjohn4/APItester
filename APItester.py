# ABC API performance benchmark before we add logging and auditing
#
# Ron Johnson 12/7/2017
#
# 1. Performance of a remote server will be tested
# 2. The current system will act as a substitute for the UI
# 3. Enough metrics will be persisted so analytics can be run
# 4. Analytics will be granualar enough to allow working with multiple API servers
# 5. The User Cases below will not conflict with each other
# 6. APItester does not replace htop
# 7. Purpose built for ABC (e.g. the url base is hardcoded)
#
# --------
# Use Case 1 - Stress my dev env
# As a developer
# I want to stress the overall intrastructure
# So that I can understand how dev changes effect the user
#
# The developer can specify how intense and for how long to stress
# No performance feedback will be given
# No performance data is persisted
#   APItester threads, target, iterations=-1, <APIdef file>
#
# --------
# Use Case 2 - Visualize performance trends
# As a Product Owner
# I want to visualize the overall system performance over datetime
# So that I can make informed product changes
#
# APItester will gather metrics and persist
# A separate app will visualize those metrics
# The current run is compared to the last 20 run and output to stdio
#   APItester threads, target, iteratons=#, <APIdef file>
#
# --------
# Use Case 3 - Performance monitoring during Builds
# As a team member
# I want to compare performance before and after specific changes
# So that I can continue to balance performance with functionality
# The current run is compared to the last 20 run and output to stdio
#   APItester threads, target, iteratons=#, <APIdef file, with 1 API enabled>
#

# Persisitence table
# -RunDateTime (same for all entries in 1 run, captured at the start of the run)
# -threads
# -target
# -iterations
# -api
# -average_duration
#
# queries
# return RunDateTime of the last x runs with the same threads, target, iterations
# return all records for a specific RunDateTime, threads, target, iterations
#
import click
import csv
import requests
import datetime
import json
from random import randrange
from threading import Thread
from APItesterDB import DB


return_config = {}
current_test_config = []
current_session = requests.session()
timestamp = str(datetime.datetime.now())


class env_variables:
    def __init__(self):
        self.networkID = None
        self.propertyID = None
        self.contentsID = None
        self.seasonID = None
        self.volumeID = None
        self.categoryID = None
        self.livefeedID = None
        self.mediaacceptprofileID = None
        self.packageID = None
        self.partnerID = None
        self.plannerID = None
        self.deliveryConditionID = None
        self.externalMetadataSourceID = None
        self.FFmpegTemplateID = None
        self.intermediateVideoTemplateID = None
        self.macCaptionTemplateID = None
        self.xlsTemplateID = None
        self.executionID = None
        self.mvpdPartnerID =  None


class parm_variables:
    def __init__(self, config, domain, threads, iterations, APIfile):
        self.config = config
        self.domain = domain
        self.threads = threads
        self.iterations = iterations
        self.APIfile = APIfile

    def __str__(self):
        return('config:{0}, domain:{1}, threads:{2}, iterations:{3}, APIfile:{4}'.format(
            self.config, self.domain, self.threads, self.iterations, self.APIfile))


@click.command()
@click.option('--domain', default='http://10.20.16.72:8080', help='Server where API is executed')
@click.option('--threads', default=10, help='Number of threads to use')
@click.option('--iterations', default=10, help='Number of times the full test is run')
@click.argument('apifile')
def APIloop(domain, threads, iterations, apifile):
    APIparms = parm_variables(apifile, domain, threads, iterations, apifile)
    print(APIparms)

    global current_session
    global current_test_config

    auth_url = domain +  '/reachengine/security/login?auth_user=system&auth_password=password&depth=-1'
    r = current_session.get(auth_url)

    ifile = open(apifile, 'r')
    reader = csv.DictReader(ifile)

    for row in reader:
        row['calls'] = 0
        row['total_duration'] = 0
        current_test_config.append(row)
        if row['Parms']:
            urlkey = row['api'] + '?' + row['Parms']
        else:
            urlkey = row['api']
        return_config[urlkey] = row

    thread_pool = []
    ifile.close()
    for t in range(APIparms.threads):
        t = Thread(target=APItestset, args=(t, APIparms))
        t.start()
        thread_pool.append(t)

    # wait for all threads to finish
    for t in thread_pool:
        t.join()

    write_datetime = datetime.datetime.now()
    print('len:', len(current_test_config))
    for r in current_test_config:
        print(r)
        db.dbwriterow(APIparms.config, write_datetime, APIparms.threads, r['calls'], APIparms.domain, r['api'], r['total_duration'])

    # def dbwriterow(self, datetime, threads, host, api, duration):


def APItestset(i, APIparms):
    # list of key, values to hold global parameters between the first call that finds the value
    # and the subsequent call that needs the value as a parameter
    current_env = env_variables()

    for i in range(APIparms.iterations):
        for row in current_test_config:
            if  row['Active'].upper()[0] == 'Y' :
                try:
                    APItest(APIparms, row['FieldToLoad'], row['SourceField'], row['api'], row['Parms'], current_env)
                except ValueError:
                    print('Unexpected error {0} while processing {1} with {2}'.format(
                        ValueError, row['api'], row['Parms']))
                    print(row)


def APItest(APIparms, FieldToLoad, SourceField, api, parms, current_env):
    global current_session

    if parms =='':
        urlkey = api
        url = APIparms.domain +  '/reachengine/api' + api
    else:
        #assume parms can contain any parameter, try them all
        urlkey = api + '?' + parms
        url = APIparms.domain + '/reachengine/api' + api + '?' + parms

    # url = 'http://10.20.16.71:8080/reachengine/api/abc/contents/5025/breakPrePostRolls'

    # print('url before:', url)
    url = url.format(
            networkID=current_env.networkID,
            propertyID=current_env.propertyID,
            contentsID=current_env.contentsID,
            seasonID=current_env.seasonID,
            volumeID=current_env.volumeID,
            categoryID=current_env.categoryID,
            livefeedID=current_env.livefeedID,
            mediaacceptprofileID=current_env.mediaacceptprofileID,
            packageID=current_env.packageID,
            partnerID=current_env.partnerID,
            plannerID=current_env.plannerID,
            deliveryConditionID=current_env.deliveryConditionID,
            externalMetadataSourceID=current_env.externalMetadataSourceID,
            FFmpegTemplateID=current_env.FFmpegTemplateID,
            intermediateVideoTemplateID=current_env.intermediateVideoTemplateID,
            macCaptionTemplateID=current_env.macCaptionTemplateID,
            xlsTemplateID=current_env.xlsTemplateID,
            executionID=current_env.executionID,
            mvpdPartnerID=current_env.mvpdPartnerID)

    # print('url after:', url)

    time_start = datetime.datetime.now()
    # print(url)
    r = current_session.get(url)
    time_stop = datetime.datetime.now()
    time_temp = time_stop - time_start

    # miliseconds
    time_duration = time_temp.total_seconds() * 1000

    if r.status_code // 100 == 2:
        if not r.text:
            print('Return Status:{0} - NO DATA RETURNED {1}'.format(r.status_code, urlkey))

        if SourceField and FieldToLoad:
            if r.text:
                # print(FieldToLoad)
                json_return = json.loads(r.text)
                # print('current_env before:', current_env)
                # current_env[FieldToLoad] = RndField(SourceField, json_return)

                setattr(current_env, FieldToLoad, RndField(SourceField, json_return))

                # print('current_env after:', current_env)
            else:
                print('FieldToLoad:{0}, but no json_return from called API {1}'.format(FieldToLoad, urlkey))

        return_config[urlkey]['calls'] += 1
        return_config[urlkey]['total_duration'] += time_duration
    else:
        print('Return Status:{0} {1}'.format(r.status_code, urlkey))


def RndField(SourceField, json_return):
    x = randrange(len(json_return))
    # print('rnd:{0}, SourceField:{1}'.format(x, SourceField))
    return(json_return[x][SourceField])



if __name__ == '__main__':
    db = DB()
    APIloop()
