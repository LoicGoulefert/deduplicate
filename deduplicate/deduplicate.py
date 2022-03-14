from typing import List, Tuple, Union

import click
import numpy as np
import vpype as vp
import vpype_cli
from shapely.geometry import MultiLineString
from tqdm import tqdm


def _deduplicate_layer(
    lines: vp.LineCollection, tolerance: float, progress_bar: bool, keep_duplicates: bool
) -> Tuple[vp.LineCollection, vp.LineCollection]:
    """Deduplicate lines of a single layer."""

    # Splitall lines into segments
    split_lines = vp.LineCollection()
    for line in lines:
        split_lines.extend(
            [line[i : i + 2] for i in range(len(line) - 1) if line[i] != line[i + 1]]
        )

    lc = vp.LineCollection()
    removed_lines = vp.LineCollection()
    line_arr = np.array([np.array(line.coords) for line in split_lines.as_mls().geoms])
    mask = np.zeros(len(line_arr), dtype=bool)

    for i, line in enumerate(tqdm(line_arr[:-1], disable=progress_bar)):
        reshaped = line.reshape(-1, 2, 2)
        # Matching start and end points
        mask[i + 1 :] |= np.all(
            np.isclose(reshaped, line_arr[i + 1 :], atol=tolerance), axis=(1, 2)
        )
        # Matching end and start points
        mask[i + 1 :] |= np.all(
            np.isclose(reshaped[:, ::-1, :], line_arr[i + 1 :], atol=tolerance),
            axis=(1, 2),
        )

    if keep_duplicates:
        removed_lines.extend(MultiLineString(list(line_arr[mask])))

    line_arr = line_arr[~mask]
    lc.extend(MultiLineString(list(line_arr)))

    return lc, removed_lines


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=vpype_cli.LengthType(),
    default="0.01mm",
    help="Max distance between points to consider them equal (default: 0.01mm)",
)
@click.option(
    "-p", "--progress-bar", is_flag=True, default=True, help="(flag) Display a progress bar"
)
@click.option(
    "-l",
    "--layer",
    type=vpype_cli.LayerType(accept_multiple=True),
    default="all",
    help="Target layer(s) (defaul: 'all')",
)
@click.option(
    "-k",
    "--keep-duplicates",
    is_flag=True,
    default=False,
    help="(flag) Keep removed duplicates in a separate layer",
)
@vpype_cli.global_processor
def deduplicate(
    document: vp.Document,
    tolerance: float,
    progress_bar: bool,
    layer: Union[int, List[int]],
    keep_duplicates: bool,
) -> vp.Document:
    """Remove duplicate lines."""

    layer_ids = vpype_cli.multiple_to_layer_ids(layer, document)
    new_document = document.empty_copy()
    removed_layer_id = document.free_id()

    for lines, l_id in zip(document.layers_from_ids(layer_ids), layer_ids):
        new_lines, removed_lines = _deduplicate_layer(
            lines, tolerance, progress_bar, keep_duplicates
        )
        new_document.add(new_lines, layer_id=l_id)

        if keep_duplicates and not removed_lines.is_empty():
            new_document.add(removed_lines, layer_id=removed_layer_id)

    return new_document


deduplicate.help_group = "Plugins"
