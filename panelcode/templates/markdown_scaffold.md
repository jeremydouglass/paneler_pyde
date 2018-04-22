# {{ pagetitle }}
_{{ datetime }}_

{% for group in panelcode | batch(10) %}

```panelcode
{% for item in group %}
{{ ";" if not loop.first }}{{ " " if loop.first }} 1.z    {: img='{{ item }}' }
{% endfor %}
{{ galleryopts }}
```
{% endfor %}
