from mjml_python import mjml_to_html

mjml_string = """
<mjml>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text>Hello World</mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

html_output = mjml_to_html(mjml_string)
print(html_output)