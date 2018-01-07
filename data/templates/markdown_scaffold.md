# {{ pagetitle }}
_{{ datetime }}_

```panelcode
{% for item in panelcode %}
{{ ";" if not loop.last }} 1z {: img='{{ item }}' }{% endfor %}
{{ galleryopts }}
```
