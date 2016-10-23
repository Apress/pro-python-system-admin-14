<h1>System checks</h1>
{% if systems %}
  {% for system in systems %}
    <h2>{{ systems[system].description }}</h2>
    <p>{{ systems[system].address }}:{{ systems[system].port }}</p>
    {% if systems[system].checks %}
      The following checks are available:
      <ul>
        {% for check in systems[system].checks %}
          <li><a href="{{ check }}.html">{{ systems[system].checks[check].description }}</a></li>
        {% endfor %}
      </ul>
    {% else %}
      There are no checks defined for this system
    {% endif %}
  {% endfor %}
{% else %}
  No system configuration available
{% endif %}
