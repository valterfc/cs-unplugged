from django.urls import reverse
from model_mommy import mommy
from tests.BaseTestWithDB import BaseTestWithDB
from tests.topics import create_topics_test_data
from topics.models import Topic


class AllCurriculumIntegrationViewTest(BaseTestWithDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "en"

    def test_all_curriculum_integration_view_with_no_integrations(self):
        url = reverse("topics:all_curriculum_integrations")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["curriculum_integrations"]), 0)

    def test_all_curriculum_integration_view_with_one_integration(self):
        topic = mommy.make(Topic)
        create_topics_test_data.create_test_integration(topic, 1)

        url = reverse("topics:all_curriculum_integrations")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["curriculum_integrations"]), 1)
        self.assertQuerysetEqual(
            response.context["curriculum_integrations"],
            ["<CurriculumIntegration: Integration 1>"]
        )

    def test_all_curriculum_integration_view_with_multiple_integration(self):
        topic = mommy.make(Topic)
        create_topics_test_data.create_test_integration(topic, 1)
        create_topics_test_data.create_test_integration(topic, 2)
        create_topics_test_data.create_test_integration(topic, 3)

        url = reverse("topics:all_curriculum_integrations")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["curriculum_integrations"]), 3)
        self.assertQuerysetEqual(
            response.context["curriculum_integrations"],
            [
                "<CurriculumIntegration: Integration 1>",
                "<CurriculumIntegration: Integration 2>",
                "<CurriculumIntegration: Integration 3>",
            ]
        )

    def test_all_curriculum_integration_view_order(self):
        topic_1 = mommy.make(Topic, name="1")
        topic_2 = mommy.make(Topic, name="2")
        create_topics_test_data.create_test_integration(topic_2, 3)
        create_topics_test_data.create_test_integration(topic_2, 2)
        create_topics_test_data.create_test_integration(topic_2, 1)
        create_topics_test_data.create_test_integration(topic_1, 4)
        create_topics_test_data.create_test_integration(topic_1, 5)
        create_topics_test_data.create_test_integration(topic_1, 6)

        url = reverse("topics:all_curriculum_integrations")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["curriculum_integrations"]), 6)
        self.assertQuerysetEqual(
            response.context["curriculum_integrations"],
            [
                "<CurriculumIntegration: Integration 4>",
                "<CurriculumIntegration: Integration 5>",
                "<CurriculumIntegration: Integration 6>",
                "<CurriculumIntegration: Integration 1>",
                "<CurriculumIntegration: Integration 2>",
                "<CurriculumIntegration: Integration 3>",
            ]
        )
