from django.db import models


class ConfigDirective(models.Model):
    class Meta:
        verbose_name = 'Configuration Directive'
        verbose_name_plural = 'Configuration Directives'
    name = models.CharField(max_length=200)
    is_container = models.BooleanField(default=False)
    documentation = models.URLField(
                       default='http://httpd.apache.org/docs/2.0/mod/core.html')

    def __unicode__(self):
        return self.name

class VirtualHost(models.Model):
    class Meta:
        verbose_name = 'Virtual Host'
        verbose_name_plural = 'Virtual Hosts'
    is_default = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False, 
                                      help_text="""Template virtual hosts are 
                                                  commented out in the configuration 
                                                  and can be reused as templates""")
    description = models.CharField(max_length=200)
    bind_address = models.CharField(max_length=200)
    directives = models.ManyToManyField(ConfigDirective, through='VHostDirective')

    def __unicode__(self):
        default_mark = ' (*)' if self.is_default else ''
        return self.description + default_mark

    def domain_names(self):
        result = ''
        primary_domains = self.vhostdirective_set.filter(directive__name='ServerName')
        if primary_domains:
            result = "<a href='http://%(d)s' target='_blank'>%(d)s</a>" % {'d': primary_domains[0].value}
        else:
            result = 'No primary domain defined!'
        secondary_domains = self.vhostdirective_set.filter(directive__name='ServerAlias')
        if secondary_domains:
            result += ' ('
            for domain in secondary_domains:
                result += "<a href='http://%(d)s' target='_blank'>%(d)s</a>, " % {'d': domain.value}
            result = result[:-2] + ')'
        return result
    domain_names.allow_tags = True

    def code_snippet(self):
        return "<a href='/%i/' target='_blank'>View code snippet</a>" % self.id
    code_snippet.allow_tags = True



class VHostDirective(models.Model):
    class Meta:
        verbose_name = 'Virtual Host Directive'
        verbose_name_plural = 'Virtual Host Directives'
    directive = models.ForeignKey(ConfigDirective)
    vhost = models.ForeignKey(VirtualHost)
    parent = models.ForeignKey('self', blank=True, null=True, 
                               limit_choices_to={'directive__is_container': True})
    value = models.CharField(max_length=200)

    def __unicode__(self):
        fmt_str = "<%s %s>" if self.directive.is_container else "%s %s"
        directive_name = self.directive.name.strip('<>')
        return fmt_str % (directive_name, self.value)

    def close_tag(self):
        return "</%s>" % self.directive.name.strip('<>') if self.directive.is_container else ""

