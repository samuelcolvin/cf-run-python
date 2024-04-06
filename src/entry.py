from io import StringIO

from js import Response, Request


async def on_fetch(request: Request, _env):
    if request.method == 'POST':
        return await run_code(request)
    else:
        return show_form()


async def run_code(request: Request,):
    data = await request.json()
    output = StringIO()

    def print_to_output(*args, **kwargs):
        kwargs['file'] = output
        print(*args, **kwargs)

    exec(data.python, {'print': print_to_output})
    return Response.new(output.getvalue())


def show_form():
    response = Response.new(
        # language=HTML
        """\
<div style="margin: 10px auto;max-width: 600px">
  <h1>CloudFlare Workers Python demo</h1>
  <form>
    <div style="margin-bottom: 5px">
      <textarea name="python" rows="16" cols="80" placeholder="Write some Python...">
from datetime import datetime
from typing import Tuple

from pydantic import BaseModel


class Delivery(BaseModel):
    timestamp: datetime
    dimensions: Tuple[int, int]


m = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])
print(repr(m.timestamp))
print(m.dimensions)
</textarea>
    </div>
    <input type="submit" value="Run">
  </form>
  <pre id="output"></pre>
  <script>
    document.querySelector('form').addEventListener('submit', async (e) => {
      e.preventDefault()
      const python = document.querySelector('textarea').value
      const response = await fetch('', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({python}),
      });
      document.querySelector('#output').textContent = await response.text()
    });
  </script>
</div>
"""
    )
    # is this really how I have to set the content type?
    response.headers.set('Content-Type', 'text/html')
    return response
