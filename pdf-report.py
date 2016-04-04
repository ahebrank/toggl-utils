import sys, os, urllib2, base64, json, argparse, re, datetime

def fetch(url, params = None):
  username = os.getenv('TOGGL_API_KEY', None)
  if username is None:
    raise KeyError('set an environmental variable TOGGL_API_KEY to your API key')
  password = "api_token"

  if isinstance(params, dict):
    url = url + '?' + '&'.join(["%s=%s" % (key, params[key]) for key in params])

  request = urllib2.Request(url)
  authstring = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % authstring)

  response = urllib2.urlopen(request)
  return response.read()

def get_json(url):
  data = fetch(url)
  return json.loads(data)

def get_client_ids(names = None):
  data = get_json("https://www.toggl.com/api/v8/clients")
  return ['%d' % client['id'] for client in data if names is None or client['name'] in names]

def get_workspace_ids():
  data = get_json("https://www.toggl.com/api/v8/workspaces")
  return ['%s' % workspace['id'] for workspace in data]

def get_pdf_report(workspace_id, clients, startdate, enddate, output_dir):
  pdf_string = fetch("https://toggl.com/reports/api/v2/summary.pdf", {
      'user_agent': 'biweekly-report-fetcher',
      'workspace_id': workspace_id,
      'since': startdate,
      'until': enddate,
      'client_ids': ','.join(clients),
      'order_field': 'duration',
      'order_desc': 'on'
    })

  fn = os.path.join(output_dir, 'Toggl_projects_%s_to_%s.pdf' % (startdate, enddate))
  with open(fn, 'wb') as fout:
    fout.write(pdf_string)
  return fn

def check_week(date, snap_start=True):
  # current date format
  match = re.search(r'\d\d\d\d\-\d\d\-\d\d', date)
  if match:
    return date

  today = datetime.datetime.today()
  
  # relative weeks?
  match = re.search(r'^-{0,1}\d+$', date)
  if match:
    day_offset = int(date) * 7
    target_date = today + datetime.timedelta(days=day_offset)

    # some messy biweekly snapping follows
    target_day = target_date.day
    target_month = target_date.month
    target_year = target_date.year
    if target_day < 7:
      if snap_start:
        target_day = 1
      else:
        target_day = 31
        target_month -= 1
    elif target_day <= 21:
      if snap_start:
        target_day = 16
      else:
        target_day = 15
    else:
      if snap_start:
        target_day = 1
        target_month += 1
      else:
        target_day = 31

    if target_month < 1:
      target_year -= 1
      target_month = 12
    if target_month > 12:
      target_year += 1
      target_month = 1

    # a little sanity check on the number of days in a month
    days_in_month = (datetime.date(target_year, target_month + 1, 1) - datetime.date(target_year, target_month, 1)).days
    target_day = min(target_day, days_in_month)
    return "%04d-%02d-%02d" % (target_year, target_month, target_day)

  # don't know what to do with this format, just use today
  return today.strftime('%Y-%m-%d')


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Pull down a PDF report from Toggl')
  parser.add_argument('-c', '--client', action='append', help='a client (may provide multiple)', default=[])
  parser.add_argument('-s', '--start', action='store', help='start date', required=True)
  parser.add_argument('-e', '--end', action='store', help='end date', required=True)
  parser.add_argument('-w', '--workspace', action='store', help='workspace ID', default=None)
  parser.add_argument('-d', '--dir', action='store', help='output directory (defaults to pwd)', default='.')
  args = parser.parse_args()

  if args.workspace is None:
    workspace_id = get_workspace_ids()[0]
  else:
    workspace_id = args.workspace

  client_ids = get_client_ids(args.client)

  # a little date validation
  since = check_week(args.start, snap_start=True)
  until = check_week(args.end, snap_start=False)

  if since > until:
    print "Date error: %s is after %s." % (since, until)
    sys.exit(1)

  output_dir = args.dir
  if not os.path.exists(output_dir):
    print "Output directory %s not found" % output_dir
    sys.exit(1)

  filename = get_pdf_report(workspace_id, client_ids, since, until, output_dir)