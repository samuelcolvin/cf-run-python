from io import StringIO
import traceback

from js import Response, Request


async def on_fetch(request: Request, _env):
    if request.method == 'POST':
        return await run_code(request)
    else:
        return show_form()


async def run_code(request: Request,):
    code = await request.text()
    output = StringIO()

    def print_to_output(*args, **kwargs):
        kwargs['file'] = output
        print(*args, **kwargs)

    try:
        exec(code, {'print': print_to_output})
    except BaseException:
        tb = traceback.format_exc()
        # remove the first frame
        lines = tb.splitlines()
        tb = '\n'.join(lines[:1] + lines[3:])

        tb = tb.replace('File "<string>"', 'Request code')
        output_value = output.getvalue()
        if output_value:
            error = f'Output:\n{output.getvalue()}\n\n{tb}\n'
        else:
            error = f'{tb}\n'
        return Response.new(error, status=400)
    else:
        return Response.new(output.getvalue())


def show_form():
    response = Response.new(
        # language=HTML
        """\
<div style="margin: 10px auto;max-width: 800px">
  <h1>Run Python</h1>
  <p><a href="https://github.com/samuelcolvin/cf-run-python">learn more.</a></p>
  <p>
    You can also run the code directly by Posting to <code>/</code>
    with the payload as code <code>print('hello world')</code>.
  </p>
  <form>
    <div style="margin-bottom: 5px">
      <textarea name="python" rows="16" style="width:100%" placeholder="Write some Python...">
import sys

print(sys.version)
print(2 ** 15)
</textarea>
    </div>
    <input type="submit" value="Run">
  </form>
  <pre id="output" style="white-space: pre-wrap; word-wrap: break-word;"></pre>
</div>
<script>
  const output = document.querySelector('#output')
  output.textContent = ''
  document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault()
    const body = document.querySelector('textarea').value
    const response = await fetch('', {method: 'POST', body});
    output.textContent = await response.text()
  });
</script>
""")
    # is this really how I have to set the content type?
    response.headers.set('Content-Type', 'text/html')
    return response
