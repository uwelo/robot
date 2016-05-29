#! /usr/bin/env python
import argparse
import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile
import time
import traceback
import urllib
import sys
import atexit

basedir = os.path.realpath(os.path.dirname(__file__) + "/..")
outdir = basedir + "/output"
profiledir = basedir + "/profiles"
selenium_log_file = None

REMOTE_URL = None
PROXY = None
BROWSERS = None
TESTS = []
TAGS = None
SERVER = None
PARALLEL_BROWSER_USAGE = False
SELENIUM_PORT = 4445
START_SELENIUM = None
VERBOSE = False
LISTENER = None
ARGS_FILE = None
TESTDATA = False

def parseArgs():
    global REMOTE_URL, PROXY, TESTS, BROWSERS, PARALLEL_BROWSER_USAGE, TAGS, START_SELENIUM, VERBOSE, LISTENER, ARGS_FILE, SERVER, TESTDATA

    parser = argparse.ArgumentParser(
        description="A highly configurable tool to execute Robot tests. (http://robotframework.org)",
        formatter_class=argparse.RawTextHelpFormatter, epilog="Happy testing!"
    )
    parser.add_argument("-t", "--tests",
        action="append",
        help="""
            The tests to run (name of a directory or a single test suite).
            Use multiple times to run multiple test suites.
            Example: %(prog)s -t tests/syi
            (default: tests)""")

    parser.add_argument("-i", "--include",
        help="""
            Include tests by tag. See pybot's include param for more details.
            Example: %(prog)s -i DHP""")

    parser.add_argument("-td", "--testdata",
        action="store_true",
        help="""
            Creates the required Test data on your Integra
            PLEASE NOTE: You cannot execute the test data test suite with other test suites""")

    parser.add_argument("-srv", "--server",
        help="""
            Base url to run your tests, can be used for local testing.
            Example: %(prog)s -srv localhost:8080""")

    parser.add_argument("-b", "--browser",
        action="append",
        help="""
            Browser to use during tests (supported: ff, chrome, phantomjs, ie, safari).
            Use argument multiple times to run tests against multiple browsers.
            Example: %(prog)s -b ff -b phantomjs

            Specify browser version (leave empty if you don't care) and
            platform (leave empty or set to ANY if you don't care) if you like.
            Example: %(prog)s -b ff:28.0:WINDOWS -b ie:9.0 -b chrome::MAC
            (default: ff)""")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--start-selenium",
        action="store_true",
        help="""
            Start selenium server before test run.
            (default)
            """)

    group.add_argument("-r", "--remote-url",
        help="""
            Use a remote URL to connect to a running selenium server.
            PLEASE NOTE: use only one --start-selenium OR --remote-url
            Example: %(prog)s -r TODO
            """)

    parser.add_argument("-p", "--proxy",
        help="""
            The proxy and port to use during tests.
            Example: %(prog)s -p 10.44.225.99:8080""")

    parser.add_argument("--no-proxy",
        action="store_true",
        help="""
            Don't use a proxy and run tests against PROD system.
            Be careful when using this!""")

    parser.add_argument("-par", "--parallel",
        action="store_true",
        help="Use if you want to run tests in parallel.")

    parser.add_argument("-v", "--verbose", action="store_true")

    parser.add_argument("-l", "--listener",
        help="""
            Listener monitoring test execution (e.g. as set by RIDE).
            Will be passed to pybot.
            """)

    parser.add_argument("--argumentfile",
        help="""
            File to parse additional arguments from (e.g. as provided by RIDE).
            Will be passed to pybot.""")
            
    (args, unknown) = parser.parse_known_args()  # ignore unknown args (e.g. those passed by RIDE)

    if args.verbose: VERBOSE = True
    if args.testdata: TESTDATA = True
    if args.proxy:
        if not ":" in args.proxy:
            print "Proxy parameter '%s' is missing port specification! Should look like: '10.44.225.99:8080'" % args.proxy
            exit(1)
        PROXY = args.proxy
    if not PROXY and not args.no_proxy:
        print "Neither proxy nor no-proxy option set. Aborting!"
        exit(1)

    if args.tests:
        for test in args.tests:
            TESTS.append(basedir + "/" + test)
    else:
        TESTS.append(basedir + "/tests")

    if args.include: TAGS = args.include
    if args.parallel: PARALLEL_BROWSER_USAGE = True
    if args.listener: LISTENER = args.listener
    if args.argumentfile: ARGS_FILE = args.argumentfile
    if args.remote_url: REMOTE_URL = args.remote_url
    if args.start_selenium: START_SELENIUM = True
    if not START_SELENIUM and not REMOTE_URL: START_SELENIUM = True
    BROWSERS = args.browser if args.browser else ["ff"]
    if args.server: SERVER = args.server

    return args

def printVersions():
    subprocess.Popen("python --version", shell=True).wait()
    subprocess.Popen("pip --version", shell=True).wait()
    subprocess.Popen("pip freeze | grep robotframework", shell=True).wait()

def startSeleniumServer():
    global selenium_log_file, REMOTE_URL,selenium_process

    # override the remote_url to ensure that our self started server will be used
    REMOTE_URL = "http://127.0.0.1:%d/wd/hub" % SELENIUM_PORT

    # start the server. only std out is redirected to the file to ensure that errors are visible in the shell directly
    selenium_log_file = open(outdir + "/selenium-server.log", "w")
    print "starting selenium server on port %d ..." % SELENIUM_PORT
    selenium_path = basedir + "/bin/run-selenium-server.sh"
    if VERBOSE: print "running %s %d" % (selenium_path, SELENIUM_PORT)
    selenium_process = subprocess.Popen([selenium_path, str(SELENIUM_PORT)], stdout=selenium_log_file)

    atexit.register(stopSeleniumServer)

    # wait until the selenium server started successfully
    counter = 0
    while not up(REMOTE_URL + "/status"):
        if counter >= 30:
            print "automatically started selenium server didn't finish booting in 30 seconds"
            print "please have a look in its log file: %s/selenium-server.log" % outdir
            exit(1)

        print "Waiting..."
        time.sleep(1)
        counter += 1

    print "selenium server started."

def up(url):
    try:
        if VERBOSE: print "checking if %s is up ..." % url
        response = urllib.urlopen(url)
        status = response.getcode()
        if VERBOSE: print "... got status code:", status
    except IOError:
        if VERBOSE: print "... got an IOError!"
        status = None
    return status == 200

def stopSeleniumServer():
    global selenium_log_file

    print "stopping automatically started selenium server ..."
    server_url = "http://127.0.0.1:%d/selenium-server/driver/?cmd=shutDownSeleniumServer" % SELENIUM_PORT
    try:
        response = urllib.urlopen(server_url)
        if response.getcode() == 200:
            print "selenium server stop requested"
        else:
            print "selenium server answered with: %d" % response.getcode()
    except:
        print "failed to stop selenium server!"

    time.sleep(1)
    selenium_process.terminate()
    selenium_log_file.close()
    print "Selenium server killed"

def runTests():
    procs = []
    exit_code_sum = 0

    if VERBOSE:
        print "Using browsers: %s" % " ".join(BROWSERS)

    if TESTDATA:
        pybot_cmd = " ".join(["pybot",
                              "--variable SERVER:%s" % SERVER if SERVER else "",
                              "--variable PROXY:%s" % PROXY if PROXY else "",
                              "--variable REMOTE_URL:%s" % REMOTE_URL,
                              "--include testdata",
                              "--loglevel DEBUG" if VERBOSE else "",
                              "--listener %s" % LISTENER if LISTENER else "",
                              "--argumentfile %s" % ARGS_FILE if ARGS_FILE else "",
                              "--log none",
                              "--report none",
                              "--outputdir %s" % outdir,
                              "--output testdata.xml",
                              " ".join(TESTS)])

        proc = subprocess.Popen(pybot_cmd, shell=True)
        print "waiting for test to finish ..."
        exit_code = proc.wait()
        print "test done. (exit code: %d)" % exit_code
        exit_code_sum += exit_code

    else:
        for index, BROWSER in enumerate(BROWSERS):
            print "Running tests %s with %s using proxy %s %s" % (TESTS, BROWSER, PROXY, "against " + SERVER if SERVER else "")
            browser_conf = BROWSER.split(":")
            browser_name = browser_conf[0]
            browser_version = browser_conf[1] if len(browser_conf) > 1 else ""
            browser_platform = browser_conf[2] if len(browser_conf) > 2 else "ANY"
            browser_conf_name = BROWSER.replace(":", "_")
            pybot_cmd = " ".join(["pybot",
                              "--variable SERVER:%s" % SERVER if SERVER else "",
                              "--variable BROWSER:%s" % browser_name,
                              "--variable BROWSER_VERSION:%s" % browser_version,
                              "--variable PLATFORM:%s" % browser_platform,
                              "--variable PROXY:%s" % PROXY if PROXY else "",
                              "--variable REMOTE_URL:%s" % REMOTE_URL,
                              "--name %s" % browser_conf_name,
                              "--include %s" % TAGS if TAGS else "",
                              "--exclude testdata",
                              "--loglevel DEBUG" if VERBOSE else "",
                              "--listener %s" % LISTENER if LISTENER else "",
                              "--argumentfile %s" % ARGS_FILE if ARGS_FILE else "",
                              "--log none",
                              "--report none",
                              "--outputdir %s" % outdir,
                              "--output %s.xml" % browser_conf_name,
                              " ".join(TESTS)])

            #if VERBOSE: print "Running %s" % pybot_cmd

            if PARALLEL_BROWSER_USAGE:
                log = NamedTemporaryFile(suffix=".log", prefix="%s_" % browser_conf_name)
                if VERBOSE: print "Capturing stdout for %s in %s ..." % (browser_conf_name, log.name)
                proc = subprocess.Popen(pybot_cmd, shell=True, stdout=log)
                procs.append((proc, log))
            else:
               proc = subprocess.Popen(pybot_cmd, shell=True)
               print "waiting for test to finish ..."
               exit_code = proc.wait()
               print "test done. (exit code: %d)" % exit_code
               exit_code_sum += exit_code






    if procs:
        print "waiting for tests to finish ..."
        for proc, log in procs:
            exit_code = proc.wait()
            exit_code_sum += exit_code
            if log:
                log.seek(0)
                shutil.copyfileobj(log, sys.stdout)
                log.close()
            print "test done. (exit code: %d)" % exit_code

    return min(exit_code_sum, 1)

def generateReports():
    # build report containing all tests runs
    print "Generating reports into %s ..." % outdir
    rebot_cmd = " ".join(["rebot",
                          "--name tests",
                          "--outputdir %s" % outdir,
                          "--output tests %s/*.xml" % outdir])
    if VERBOSE: print "Running %s" % rebot_cmd
    proc = subprocess.Popen(rebot_cmd, shell=True)
    return proc.wait()

#### MAIN
def main():
    print "Running script ..."
    parseArgs()
    if VERBOSE: printVersions()

    # ensure a clean but existing directory for log files and our final report files
    if os.path.exists(outdir):
        if VERBOSE: print "deleting previous output directory: %s" % outdir
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    print "created new output directory: %s" % outdir

    if START_SELENIUM:
        startSeleniumServer()

    # make sure selenium server is stopped even if exceptions occur during test execution
    try:
        exit_code = runTests()
        exit_code += generateReports()
    except:
        print traceback.format_exc()
        print "Test execution failed with exception!", sys.exc_info()[0]
        exit_code = 1

    print "Done."
    exit(min(exit_code, 1))

if __name__ == "__main__":
    main()
