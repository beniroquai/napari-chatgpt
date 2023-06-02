import traceback

import numpy
from arbol import asection, aprint
from imageio.v3 import imread
from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.strings.find_integer_in_parenthesis import \
    find_integer_in_parenthesis
from napari_chatgpt.utils.web.duckduckgo import search_images_ddg


class WebImageSearchTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "WebImageSearchTool"
    description = (
        "Use this tool to open various types of images, such as photographs, paintings, drawings, "
        "maps, or any other kind of image, in the software called napari. "
        "Input must be a plain text web search query suitable to find the relevant images. "
        "You must specify the number of images you want to open in parentheses. "
        "For example, if the input is: 'Albert Einstein (2)' then this tool will open two images of Albert Einstein found on the web."
    )
    prompt: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        with asection(f"WebImageSearchTool: query= {query} "):

            # Parse the number of images to search
            result = find_integer_in_parenthesis(query)

            # Identify search query from nb of images:
            if result:
                search_query, nb_images = result
            else:
                search_query, nb_images = query, 1

            # Basic Cleanup:
            search_query = search_query.strip()
            nb_images = max(1, nb_images)

            # Search for image:
            results = search_images_ddg(query=search_query)

            aprint(f'Found {len(results)} images.')

            # Extract URLs:
            urls = [r['image'] for r in results]

            # Limit the number of images to open to the number found:
            nb_images = min(len(urls), nb_images)

            # Keep only the required number of urls:
            urls = urls[:nb_images]

            # open each image:
            number_of_opened_images = 0
            for i, url in enumerate(urls):
                try:
                    aprint(f'Trying to open image {i} from URL: {url}.')
                    image = imread(url)
                    image_array = numpy.array(image)
                    viewer.add_image(image_array, name=f'image_{i}')
                    number_of_opened_images += 1
                    aprint(f'Image {i} opened!')
                except Exception as e:
                    # We ignore single failures:
                    aprint(f'Image {i} failed to open!')
                    traceback.print_exc()

            if number_of_opened_images > 0:
                message = f"Opened {number_of_opened_images} images in napari out of {len(urls)} found."
            else:
                message = f"Found {len(urls)} images, but could not open any! Probably because of a file format issue."

            with asection(f"Message:"):
                aprint(message)

            return message
