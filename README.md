# APItester

APItester does just that.  A list of API endpoints and their associated query parameters and parsable return values are defined in csv (I use Excel to manage the csv).  This list is executed in the order and repetition specified.  The resulting execution times are captured to the DB for analysis.

The order of execution is important, the parsable return values can be used is subsequent calls.

APItester.py - executes the test defined API endponts.  It takes the following command line parms:
--domain - default='http://10.20.16.72:8080, Server where API is executed
--threads - default=10, Number of threads to use
--iterations - default=10, Number of times the full test is run
apifile - the path to the API configurations in csv format

APITesterUI.py - is a framework that displays the results from the persisted DB.  The data is time based and saved per API endpoint.  This allows time based analysis or display.
