"""
Offline GPX and GeoJSON Trail Exporter
Allows offline export of trails and waypoints into open formats.
Compatible with OsmAnd, Organic Maps, Garmin, and QGIS without proprietary dependencies.
"""
from typing import Dict, List, Optional
from xml.sax.saxutils import escape


def export_breadcrumbs_to_gpx(breadcrumbs: List[Dict],
                               trail_name: str = "WalkBacker Expedition",
                               description: str = "Touch Grass Nature Walk") -> str:
    """
    Format a list of GPS coordinates into standard GPX 1.1 XML format.
    """
    gpx_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="WalkBacker Open-Source AI (Touch Grass)"',
        '     xmlns="http://www.topografix.com/GPX/1/1"',
        '     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">',
        f'  <metadata>',
        f'    <name>{escape(trail_name)}</name>',
        f'    <desc>{escape(description)}</desc>',
        f'  </metadata>'
    ]

    # Add Waypoints (Origin and marked points)
    if breadcrumbs:
        origin = breadcrumbs[0]
        gpx_lines.append(f'  <wpt lat="{origin["lat"]}" lon="{origin["lon"]}">')
        gpx_lines.append(f'    <name>Origin / Trailhead</name>')
        gpx_lines.append(f'    <desc>WalkBack Target Base</desc>')
        gpx_lines.append(f'  </wpt>')

    # Add Track
    gpx_lines.append('  <trk>')
    gpx_lines.append(f'    <name>{escape(trail_name)}</name>')
    gpx_lines.append('    <trkseg>')
    for pt in breadcrumbs:
        lat = pt.get("lat")
        lon = pt.get("lon")
        time_str = pt.get("timestamp")
        ele = pt.get("elevation")

        gpx_lines.append(f'      <trkpt lat="{lat}" lon="{lon}">')
        if ele is not None:
            gpx_lines.append(f'        <ele>{ele}</ele>')
        if time_str:
            gpx_lines.append(f'        <time>{time_str}</time>')
        gpx_lines.append('      </trkpt>')
    gpx_lines.append('    </trkseg>')
    gpx_lines.append('  </trk>')
    gpx_lines.append('</gpx>')

    return "\n".join(gpx_lines)


def export_breadcrumbs_to_geojson(breadcrumbs: List[Dict],
                                   trail_name: str = "WalkBacker Expedition") -> Dict:
    """
    Format breadcrumbs into standard RFC 7946 GeoJSON FeatureCollection.
    """
    coordinates = [[pt["lon"], pt["lat"]] for pt in breadcrumbs]
    features = []

    if breadcrumbs:
        # Origin point feature
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [breadcrumbs[0]["lon"], breadcrumbs[0]["lat"]]
            },
            "properties": {
                "name": "Trailhead / Home Base",
                "role": "origin"
            }
        })

    # LineString track feature
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {
            "name": trail_name,
            "point_count": len(breadcrumbs)
        }
    })

    return {
        "type": "FeatureCollection",
        "features": features
    }
