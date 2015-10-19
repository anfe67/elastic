from django.core.management.base import BaseCommand
import random
import names

from elasticsearch.client import IndicesClient
from elasticsearch import Elasticsearch
from model_mommy import mommy
from elastic_json.models import Student, University, Course
from elastic_json.utils.bulk import put_all_to_index


class Command(BaseCommand):
    help = "generates dummy data for testing/show purposes."

    def handle(self, *args, **options):
        Student.objects.all().delete()
        University.objects.all().delete()
        Course.objects.all().delete()

        # database part
        # make some Universities
        universities = []
        for _ in range(10):
            uni = mommy.make(University)
            universities.append(uni)
        # make some courses
        template_options = ['CS%s0%s', 'MATH%s0%s', 'CHEM%s0%s', 'PHYS%s0%s']
        courses = []
        for num in range(1, 10):
            for course_num in range(1, 5):
                for template in template_options:
                    name = template % (course_num, num)
                    course = mommy.make(Course, name=name)
                    courses.append(course)
        for _ in xrange(100):
            stud = mommy.make(
                Student,
                university=random.choice(universities),
                first_name=names.get_first_name(),
                last_name=names.get_last_name(),
                age=random.randint(17, 25)
            )
            for _ in range(random.randint(1, 10)):
                index = random.randint(0, 143)
                stud.courses.add(courses[index])

        # recreate index
        indices_client = IndicesClient(client=Elasticsearch())
        indices_client.delete(index='django')
        body = {
            'mappings': {'student': Student._meta.es_mapping}
        }
        indices_client.create(index='django', body=body)

        # update part
        put_all_to_index(Student)
