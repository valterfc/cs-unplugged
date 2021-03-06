"""Module for the custom Django makeresources command."""

import os
import os.path
from urllib.parse import urlencode
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.http.request import QueryDict
from django.conf import settings
from resources.models import Resource
from resources.utils.get_resource_generator import get_resource_generator
from resources.utils.resource_valid_configurations import resource_valid_configurations
from resources.utils.resource_parameters import EnumResourceParameter


class Command(BaseCommand):
    """Required command class for the custom Django makestaticresources command."""

    help = "Creates static PDF files of resource combinations."

    def add_arguments(self, parser):
        """Add optional parameter to makeresources command."""
        parser.add_argument(
            "resource_name",
            nargs="?",
            default=None,
            help="The resource name to generate",
        )

    def handle(self, *args, **options):
        """Automatically called when the makeresources command is given."""
        base_path = settings.RESOURCE_GENERATION_LOCATION
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if options["resource_name"]:
            resources = [Resource.objects.get(name=options["resource_name"])]
        else:
            resources = Resource.objects.order_by("name")

        for resource in resources:
            print("Creating {}".format(resource.name))

            # TODO: Import repeated in next for loop, check alternatives
            empty_generator = get_resource_generator(resource.generator_module)
            if not all([isinstance(option, EnumResourceParameter)
                        for option in empty_generator.get_options().values()]):
                raise TypeError("Only EnumResourceParameters are supported for pre-generation")
            valid_options = {option.name: list(option.valid_values.keys())
                             for option in empty_generator.get_options().values()}
            combinations = resource_valid_configurations(valid_options)
            progress_bar = tqdm(combinations, ascii=True)
            # Create PDF for all possible combinations
            for combination in progress_bar:
                if resource.copies:
                    combination["copies"] = settings.RESOURCE_COPY_AMOUNT
                requested_options = QueryDict(urlencode(combination, doseq=True))
                generator = get_resource_generator(resource.generator_module, requested_options)
                (pdf_file, filename) = generator.pdf(resource.name)

                filename = "{}.pdf".format(filename)
                pdf_file_output = open(os.path.join(base_path, filename), "wb")
                pdf_file_output.write(pdf_file)
                pdf_file_output.close()
