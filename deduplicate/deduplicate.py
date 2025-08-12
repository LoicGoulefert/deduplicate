from typing import List, Tuple

import click
import vpype as vp
import vpype_cli

from shapely import union_all
from shapely.geometry import LineString, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree
from tqdm import tqdm


def _flatten_lines(geometries: List[BaseGeometry]) -> List[LineString]:
    """
    Takes a list of possibly nested geometries and flattens it into a clean list of LineStrings.

    Geometric operations can result in collections like MultiLineString. This utility function
    unpacks those collections and filters out any empty geometries, ensuring the final output
    is a simple list of valid LineString objects.

    Args:
        geometries: A list of Shapely geometry objects.

    Returns:
        A flattened list containing only non-empty Shapely LineString objects.
    """
    out = []
    # Iterate through each geometry in the input list.
    for geom in geometries:
        # If the geometry is a simple, non-empty LineString, add it directly.
        if isinstance(geom, LineString) and not geom.is_empty:
            out.append(geom)
        # If it's a MultiLineString, iterate through its sub-geometries.
        elif isinstance(geom, MultiLineString):
            # Extend the output list with only the non-empty LineStrings from the collection.
            out.extend([g for g in geom.geoms if isinstance(g, LineString) and not g.is_empty])
    return out


def _deduplicate_layer(
    lines: vp.LineCollection,
    tolerance: float,
    progress_bar: bool,
    keep_duplicates: bool,
    mask: List[BaseGeometry],
) -> Tuple[List[LineString], List[LineString], List[BaseGeometry]]:
    """
    Deduplicates lines for a single layer against a provided, persistent mask of geometries.

    This function is the core of the deduplication logic. It processes one layer at a time,
    using a spatial index (STRtree) for efficiency. It is designed to be stateful by
    accepting and returning a 'mask' of areas already covered by lines, allowing for
    deduplication across multiple layers.

    Args:
        lines: The collection of lines to process for the current layer.
        tolerance: The buffer distance around lines to consider as the overlapping area.
        progress_bar: Flag to control the display of the progress bar.
        keep_duplicates: Flag to determine if removed segments should be collected.
        mask: A list of geometries representing areas already processed.

    Returns:
        A tuple containing:
        - A list of a kept (deduplicated) LineStrings.
        - A list of removed LineStrings.
        - The updated mask including the lines from the current layer.
    """
    # These lists will collect the geometric results.
    kept_lines = []
    removed_lines_output = []

    # Invert the progress_bar flag for compatibility with the parent caller's expectation.
    progress_bar = not progress_bar

    # Set up the iterable with or without a tqdm progress bar.
    iterable = tqdm(lines, desc="Deduplicating lines") if progress_bar else lines

    # Process each line in the layer.
    for line in iterable:
        # Convert vpype's complex-number-based line into a Shapely LineString.
        linestring = LineString([(pt.real, pt.imag) for pt in line])

        # If the mask is empty (i.e., this is the very first line being processed),
        # there's nothing to deduplicate against. Keep the line and update the mask.
        if not mask:
            kept_lines.append(linestring)
            mask.append(linestring.buffer(tolerance))
            continue

        # Create a spatial index from the current mask for efficient querying.
        tree = STRtree(mask)
        # Query the tree to find only the geometries in the mask that are near the current line.
        nearby_buffers_indices = tree.query(linestring)

        # Check the .size of the NumPy array to unambiguously see if it's empty.
        # This fixes the "ValueError: The truth value of an array is ambiguous".
        if nearby_buffers_indices.size == 0:
            # If no nearby geometries are found, the line is unique. Keep it.
            kept_lines.append(linestring)
        else:
            # If there are nearby geometries, create a local mask by uniting only those.
            # This is much more performant than uniting the entire global mask.
            nearby_buffers = [mask[i] for i in nearby_buffers_indices]
            local_mask = union_all(nearby_buffers)
            
            # Calculate the portion of the line that does NOT overlap with the local mask.
            diff = linestring.difference(local_mask)

            # Keep the non-overlapping parts.
            if isinstance(diff, (LineString, MultiLineString)) and not diff.is_empty:
                kept_lines.append(diff)

            # If requested, calculate and store the overlapping (removed) parts.
            if keep_duplicates:
                # The removed portion is the intersection of the line and the local mask.
                removed_portion = linestring.intersection(local_mask)
                if isinstance(removed_portion, (LineString, MultiLineString)) and not removed_portion.is_empty:
                    removed_lines_output.append(removed_portion)

        # IMPORTANT: Add the buffer of the original, full linestring to the mask.
        # This ensures future lines are checked against the entirety of this line.
        mask.append(linestring.buffer(tolerance))

    # Clean up the collected geometries, unpacking any MultiLineStrings.
    final_kept = _flatten_lines(kept_lines)
    final_removed = _flatten_lines(removed_lines_output)

    # Return the results and the updated mask for the next function call.
    return final_kept, final_removed, mask



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
    help="Target layer(s) (default: 'all')",
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
    layer: vpype_cli.LayerType,
    keep_duplicates: bool,
) -> vp.Document:
    """Remove duplicate lines across one or more layers."""

    layer_ids = vpype_cli.multiple_to_layer_ids(layer, document)
    new_document = document.empty_copy()
    persistent_mask = []
    all_removed_lines = []

    if layer != "all":
        for l_id in document.layers:
            if l_id not in layer_ids:
                new_document.add(document.layers[l_id], layer_id=l_id)

    for l_id in layer_ids:
        if l_id not in document.layers:
            continue
            
        lines = document.layers[l_id]
        
        new_lines, removed_lines, updated_mask = _deduplicate_layer(
            lines, tolerance, progress_bar, keep_duplicates, persistent_mask
        )

        persistent_mask = updated_mask

        if new_lines:
            new_document.add(vp.LineCollection(new_lines), layer_id=l_id)
        
        if keep_duplicates and removed_lines:
            all_removed_lines.extend(removed_lines)

    if keep_duplicates and all_removed_lines:
        removed_layer_id = document.free_id()
        new_document.add(vp.LineCollection(all_removed_lines), layer_id=removed_layer_id)

    return new_document


deduplicate.help_group = "Plugins"
