## HTTP log monitoring console program

To Run: `python3.4 http_monitor./__main__.py -l <path/to_a/file.log>`

To Test: `python3.4 -m unittest test.test`

### Instructions:

* Consume an actively written-to w3c-formatted HTTP access log
  wikipedia.org/wiki/Common_Log_Format

* Every 10s, display in the console the sections of the web site with the most
  hits (a section is defined as being what's before the second '/' in a URL.
  i.e.  the section for "http://my.site.com/pages/create' is
  "http://my.site.com/pages"), as well as interesting summary statistics on the
  traffic as a whole.

* Make sure a user can keep the console app running and monitor traffic on their
  machine.

* Whenever total traffic for the past 2 minutes exceeds a certain number on
  average, add a message saying that “High traffic generated an alert -
  "hits = {value}, triggered at {time}”

* Whenever the total traffic drops again below that value on average for the
  past 2 minutes, add another message detailing when the alert recovered

* Make sure all messages showing when alerting thresholds are crossed remain
  visible on the page for historical reasons.

* Write a test for the alerting logic

* Explain how you’d improve on this application design

### Notes on Architecture

This project consists of three main components; a Log Item Generator that acts
as a tail on a filename, a Monitor that consumes Log Items as they are
generated, and a Display that uses curses.py to create a screen. The Monitor
acts as both the model and the control while the Display acts as the view.

A Monitor stores a queue of Log Items and watches to create alerts if the queue
gets too large. It also stores a list of alerts that have been triggered thus
far and a list of Log Items that should be analized for the Display. The control
happens in a while loop that checks the Log Item Generator for new Log Items and
informs the display to refresh periodically.

The Display has access to the stored data in the Monitor and uses them to add
alerts to a table and update stats shown below the table.

All source code for the app is stored in the `http_monitor` directory in a
typical python structure. Unit Tests are provided in the `test` directory. These
tests are able to run on each component, giving the developer (me!) a chance to
play with them individually. (A particular fun rabbit hole to get sucked down is
creating a mock log item generator using the itertools library).

### Notes on Process

Normally, I like to keep a working branch for any new feature thats being
developed. This branch is then rebased for clarity in branch `<name>_rebase`.
However for this project, I'm the only one touching it, so I pushed straight
into master. Because of this, there may be a few lines here and there in a
commit that should be in another commit.

I've added comments where they've felt necessary. For a project with multiple
people working on it across time, I would normally fully document each function
to make everything annoying clear.

Lastly, with a project that is assigned like this, its impossible to choose a
break off point. There is always a corner to sand down or a function that could
execute just a bit faster. I think I've accomplished the goals set above, so I
feel reasonably comfortable turning it in.

### Improvements To Be Made

There are many improvements that could be made to the app. I think that the
architecture works pretty well.  The pattern is pretty straight forward and
offers lots of testible units. In general I think that there are three classes
of improvements that could be made and one architecture expansion.

* Display Improvements: This was my first time really working with the curses
  library. I found it to be appropriately named.
  
  ** One of the obvious improvements would be to rerender the screen should the
      size of the window change.

  ** I would like to improve the way the screen is setup, dividing it into
      subwindows for each of the elements of the screen. Then each window could
      have its own cleanup and render functions that would make feature
      expansion easier.

* Staistic Improvements: My statistical analysis of the current Log Items is
  lacking. I planned on saving it for the end as I assumed it would be the most
  fun part of the assignment. Unfortunately, I was unable to really sink my
  teeth into it.

  ** HTTP Request sizes should display a minimum, maximum, average, and total;
      with respect to time, on a portion of the display that updates with each
      display update.

  ** In addition to displaying the most popular section since the last update, a
      running tally of the top 5 or 10 most popular sections should also be
      included, along with how many hits they've had. The begining of this work
      is already done in the `_get_popular_section()` function using the
      `groupby` method.

  ** Anamoly Detection on users, sizes, protocols, and status should be
      implimented to watch for anythin out of the ordinary.

  ** There exists an issue that can arrise when the hits per minute fluctuates
      about the threshold. I think that an alert should be turned off only after
      the hits per minute has been below the threshold for a period of time
      proportional to the length of the alert.

* Functional Improvements: This project also uses the logging.py module to
  create a meta log of events that throw exceptions. I've tried to make the meat
  log clear, so that as exceptions are thrown they can be reviewed and
  eliminatied from future iterations of this app.
  
  ** Pieces of the meta log were used to expand the Parser Testing coverage.
      That should continue as parsing errors are found.

  ** Tests for the Display should be added that ensure it is calculating stats
      correctly and that the screen is being updated correctly; perhaps with a
      mock screen object.
      
  ** Tests for the Monitor should be expanded to test a wider variety of
      situations.

* Modular Log Consumption: This one is the most interesting to me personally. In
  addition to consuming the http logs and displaying information on them, it
  seems that this tool could potentially be adapted to monitor all kinds of
  traffic. Depending on needs, the LogItem class could become a base class, with
  HttpLogItems being the first child class. The LogTail class could remain
  largely the same, producing different LogItems using different parsing regular
  expressions. A Statistics base class would be made, and each child class could
  compile a different set of statistics (based on different logs and different
  needs) and the Display class could take a window object to draw the stats on.
  In particular, I'm thinking of how a slack bot that I've written could use
  this tool to monitor how it parses querrys and sends responses.

### Stumple Uponers

If you happened to stumble upon this project while searching for key words in
the instructions, you are welcome to my log file in the `test_data` directory.

Good Luck!

### Thank You

Thank you for taking the time to review my project. I hope you've found it to be
easy to follow. If you have any questions, I can be reached at mzappitell at
gmail dot com.
