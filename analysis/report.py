__author__ = 'christopher'

import sys, os, csv, jinja2

data = [line for line in csv.DictReader(open(sys.argv[1], 'rb'))]

# Change the default delimiters used by Jinja such that it won't pick up
# brackets attached to LaTeX macros.
report_renderer = jinja2.Environment(
  block_start_string = '%{',
  block_end_string = '%}',
  variable_start_string = '%{{',
  variable_end_string = '%}}',
  loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

template = report_renderer.get_template('report_template.tex')

output = file(sys.argv[2], 'w')
output.write(template.render(data = data))
output.close()