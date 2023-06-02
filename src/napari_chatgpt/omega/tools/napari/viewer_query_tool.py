"""A tool for controlling a napari instance."""
from contextlib import redirect_stdout
from io import StringIO

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.python.dynamic_import import dynamic_import

_napari_viewer_query_prompt = """
"
**Task:**
Your task is to write Python code that can query an already instantiated napari viewer instance based on a plain text request. The code should be able to perform various operations such as returning information about the state of the viewer, the layers present, the dtype or shape of an image, and analyzing the content of different layers. For example, you can count the number of segments in a labels layer using the np.unique function, retrieve characteristics of individual segments like centroid coordinates, area/volume, or return statistics about the shape, area/volume, and positions of segments. You may also collect diverse measurements and statistics about segments in a labels layer.

To answer the request, you need to implement a Python function called `query(viewer)` which takes the napari viewer as a parameter and returns a string. This string will be the answer to the request.

**Here are some additional notes to help you determine which layer is referred to:**
- If the request mentions 'this/that/the image (or layer)', it most likely refers to the last added layer.
- If you are unsure about the layer being referred to, assume it is the last layer of the type most appropriate for the request.
- If the request mentions the 'selected image', it most likely refers to the active or selected image layer.
- To get the selected layer use: viewer.layers.selection.active

**Instructions for using the napari viewer:**
- The napari viewer instance is readily available using the variable 'viewer'.
- For example, you can directly access properties like 'viewer.layers[0].data.shape' without any additional code.
- Therefore, DO NOT use 'napari.Viewer()' or 'gui_qt():' in your code.
- It is important NOT to create a new instance of a napari viewer. Use the one provided in the variable 'viewer'.
- Ensure that your calls to the viewer are correct.

{generic_codegen_instructions}
- DO NOT call the 'query(viewer)' function yourself.
- Please provide your answer in Markdown format.
- Write the `query(viewer) -> str` function that takes the viewer as a parameter and returns the response.

{last_generated_code}

**Request:**
{input}

**Answer in markdown:**
"""


class NapariViewerQueryTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariViewerQueryTool"
    description = (
        "Use this tool when you require information about the napari viewer, "
        "its state, or its layers (images, labels, points, tracks, shapes, and meshes). "
        "Input must be a clear plain text description of what you want to know. "
        "The input must not assume knowledge of our conversation and must be explicit about what is asked. "
        "For instance, you can request to 'list all layers in the viewer'. "
        "Do NOT include code in your input."
    )
    prompt = _napari_viewer_query_prompt
    save_last_generated_code = False

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        with asection(f"NapariViewerQueryTool: query= {query} "):
            # prepare code:
            code = super()._prepare_code(code, do_fix_bad_calls=True)

            # Load the code as module:
            loaded_module = dynamic_import(code)

            # get the function:
            query = getattr(loaded_module, 'query')

            # Redirect output:
            f = StringIO()
            with redirect_stdout(f):
                # Run query code:
                response = query(viewer)

            # Get captured stdout:
            captured_output = f.getvalue()

            # Message:
            message = f"Tool completed query successfully, here is the response:\n\n{response}\n\nand the captured standard output:\n\n{captured_output}\n\n"

            with asection(f"Message:"):
                aprint(message)

            return message
