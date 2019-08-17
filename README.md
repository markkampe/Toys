# Introduction to CLI, Eclipse, and Java

## Learning Goals

* Introduction to the shell command line interface.
* Introduction to Eclipse.
* Introduction to Github and assignment repos.
* Building and running simple Java programs.
* Project Submission (committing changes and pushing them back to github)

## Key Terms and Concepts
* `CLI` - [Command Line Interface](https://en.wikipedia.org/wiki/Command-line_interface): running 
   programs by typing commands and arguments to a command intepreter like 
   the Linux/OSX [shell](https://en.wikipedia.org/wiki/Unix_shell).
* `Eclipse` - an [Integrated Development Environment](https://en.wikipedia.org/wiki/Integrated_development_environment) 
   that includes powerful tools for editing, running, and debugging programs.  
   In this course we will be using it as a Java IDE.
* `Git` - a distributed [version control system](https://en.wikipedia.org/wiki/Version_control) 
   for tracking coordinating and exchanging file updates among groups of collaborating developers.
* `Github` - a web-based version control and collaboration platform for software
   developers, particularly popular for Open Source projects and other shared
   code efforts.

## Overview
The goals  of this assignment are to:
   1. learn to run a few basic commands in a Linux/OSX terminal window.
   2. bring up Eclipse as an Integrated Development Environment.
   3. establish (if you do not already have one) a free personal
      [github account](https://help.github.com/en/articles/signing-up-for-a-new-github-account).
   4. import a cloned of the master-copy for this project into Eclipse.
   5. fill in the missing code in a simple Java program.
   6. submit your work by committing and pushing it back to github.

## Classes

In this project you will be making simple changes to complete a program
that is comprised of two classes:

### `Token`
A `Token` is a virtual chip with a (randomly chosen) `color` and `value`.
   - It supports methods to `get` and `set` both the `color` and `value`.
   - It supports a `toString` method to enable it to be printed.
   - It also includes a `main` method that can be used (if this
     class is run as an application) to exercise this implementation.

### `Bag`
A `Bag` is a set of `Token`s, with several methods (all of whose implementations
require the enumeration of the `Token`s in the set.  It supports several
methods:
   - `firstChip` ... print out the first `Token` in the `Bag`.
   - `allChips` ... print out all of the `Tokens` in the `Bag`.
   - `allChipsWhile` ... the same as `allChips`, but to be implemented as a while loop.
   - `addChips` ... the sum of the values of all `Tokens` in the `Bag`.
   - `chipHighValue` ... the number of high-value `Tokens` in the `Bag`.
   - `firstGreen` ... the index of the first `green` `Token` in the `Bag`.
   - This class also has a `main` method that can be used to exercise
     the functionality of the other methods.

As provided, several of these methods are incomplete (and have **// TODO** comments explaining
what needs to be done).  You are to fill in the missing code (mostly a few simple
assignments and loops) to complete all of the methods so that they work correctly.

## Getting Started

1. Click the terminal window icon on the Desktop menu bar.  A new window
   with a shell prompt will appear.  Create a new workspace directory
   on your desktop, by typing the following commands:
```
cd Desktop
mkdir CS062_Workspace
```
   after which an icon for the new folder should appear on your Desktop.

2. If you do not already have a github account, go to github.com and
   [register a new personal user account](https://help.github.com/en/articles/signing-up-for-a-new-github-account).

3. You should have received an email invitation to join the github group
   for this course.  If you follow the link in that message, it will take
   you to a screen that gives you the opportunity to accept that inviation.
   Once you are a member of the course github group you will be able to
   access assignments and submit your solutions.

4. Start Eclipse on your local machine.  It will ask you to choose
   a workspace.   You should browse to the workspace folder that you 
   created above.  Eclipse will remember this selection
   and prompt it as a default (or in the list of Recent Workspaces)
   when you start Eclipse in the future.

5. From the `File` item on the top menu bar, select `Import`.
   Scroll down to the `Git` sub-items, select the `Projects from Git`
   sub-item, and press the `Next` button.

   FIX THIS STEP IS WRONG - WE WANT TO OPERATE IN A CLONED COPY

   Select the `Clone URI` option, and *paste* the URL for the master
   repo (for this assignment).  You will also have to add your Github user
   name and password (which you have the option of telling Eclipse to
   remember).

   Select `master` as the branch to be imported.

   As a Destination, browse to the workspace directory that you 
   created in above, and click the `Next` button.

   Select `Import existing Eclipse projects` and click the `Next` button.

   After you have provided all of the required information, you will be
   able to click the `Finish` button.
   Eclipse will make a clone of the selected project into your
   current workspace, after which you should be able to view,
   edit, build and run the included software.

6. Edit the `Token.java` and `Bag.java` files to add the missing code (which
   is indicated by **// TODO** comments).  If you are not yet sure how to code
   a particular type of statement (e.g. a Java `for` loop), Google for examples
   or ask the instructor for assistance.

   If your program contains any obvious syntax errors, Eclipse will give you
   red warning indications on the affected lines of code.  If the errors are
   distributed over multiple modules you can see all of them by selecting the
   `Problems` tab in the bottom part of the Eclipse window.
   
   If you want to try compiling and running one of your programs:

      - select (in the *Package Explorer* on the left) the module you want to
        compile and run.
      - select the `Run` item from the top menu bar.
      - the output from your program should appear in the `Console` tab
        of the bottom part of the Eclipse window.

## Submitting your work

7. *Commit* your changes and *Push* them back to Github.
   
   If you select the `Git Staging` tab for the bottom part of the
   Eclipse window, you will see a list of *Unstaged Changes* 
   (changes you have made but not yet *committed*).  
   If you highlight one (or more) of those files you can
   add a commit message (describing the changes you have made) and then
   click the `Commit` button.  You can make as many *commits* as you like.
   It is common to do different *commits* for different sets of changes,
   but they will only be on your local machine until you do a *Push* back
   to the [origin](https://www.git-tower.com/learn/git/glossary/origin) on github.

   When you click the `Push` (or `Commit and Push`) button, all committed
   changes will be pushed back to Github ... at which they will be saved
   and visible to us.  We will notice and grade your last on-time *commit*.

## Helpful Considerations

* Saving your work - Make sure to commit and push your work to GitHub MULTIPLE TIMES throughout the process! Not only does this help us see your unique progress, but it ensures that you have frequent backups of your work.

## Grading
Your submission will be graded based on the following criteria:

| Criterion                                         | Points |
| :------------------------------------------------ | :----- |
| programs compile with no errors                   | 1      |
| all Token methods work correctly                  | 3      |
| all Bag methods work correctly                    | 3      |
| submitted correctly                               | 2      |
| [Style and formatting*](https://github.com/pomonacs622018f/Handouts/blob/master/style_guide.md)                               | 1      |
| **Total**                                         | **10** |

\* Code Style and Formatting refers to the correct use of Java constructs including booleans, loop constructs, etc. Think of it as good writing style for programs.

NOTE: Code that does not compile will not be accepted! Make sure that your code compiles and runs before submitting it.

You must comment your code. We will be using the JavaDoc commenting style. To be compliant with JavaDoc, you must have the following:

   Each comment on a method or class should start with `/**` and end with `**/`. 
   Every line in between should start with a `*` and be appropriately indented. 
   (Comments on variables and constants do NOT have to use this style unless they are public.)

   A comment describing the class right before the class declaration 
   (i.e. after the `import` statements). This comment should include the `@author` tag 
   after the class description, and the `@version` tag after the author tag.

   A comment for each method describing what the method does. 
   This comment should describe the what but not the how.
   `@param`, `@return` and `@throws` tags for each method (when appropriate)
   `pre-` and `post`- conditions as appropriate

Double-check that your work is indeed pushed in Github! It is your responsibility to ensure that you do so before the deadline.
