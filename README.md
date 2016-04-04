# [Toggl](https://toggl.com/) Utilities

Generate timesheet PDF reports via the [Toggl API](https://github.com/toggl/toggl_api_docs).

Simplify generation of fixed date-range reports for a fixed set of clients.  Includes some handy but possibly buggy 
date snap-to functionality to try to get, for example, the first or second half of a particular month.

If you have multiple [workspaces](https://support.toggl.com/workspace/), the script grabs the first it can find.  
To override, pass parameter `-w <WORKSPACE_ID>`.

## Example usage:

List available parameters with:

```
python pdf-report.py -h
```

For example usage, see the *.sh.example file or:

Grab the last two weeks for a particular set of clients

```
python pdf-report.py -c "General Motors" -c "Pepsi" -s -2 -e 0
```

Grab a fixed date range for all clients:

```
python pdf-report.py -s 2016-01-16 -e 2016-02-15
```
