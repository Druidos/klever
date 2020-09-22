#
# Copyright (c) 2019 ISP RAS (http://www.ispras.ru)
# Ivannikov Institute for System Programming of the Russian Academy of Sciences
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from django.db import migrations, models

import bridge.utils
import reports.models


class Migration(migrations.Migration):
    dependencies = [('reports', '0001_initial')]

    operations = [
        migrations.CreateModel(name='SourceCodeCache', fields=[
            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('identifier', models.CharField(db_index=True, max_length=256)),
            ('file', models.FileField(upload_to=reports.models.source_code_path)),
            ('access_date', models.DateTimeField(auto_now=True)),
        ], options={'db_table': 'cache_source_code'}, bases=(bridge.utils.WithFilesMixin, models.Model)),
    ]
