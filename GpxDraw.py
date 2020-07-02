import sys
from math import floor

import gpxpy
import click
import os
import html
import datetime

@click.command()
@click.option("--output", default="map", help="Specify the name of the output file. Defaults to `map`")
@click.option("--input", default="gpx", help="Specify an input folder. Defaults to `gpx`")

def main(output, input):
    load_points_and_polygon(input)
    
def format_time(time_s: float) -> str:
    if not time_s:
        return 'n/a'
    else:
        minutes = floor(time_s / 60.)
        hours = floor(minutes / 60.)
        return '%s:%s:%s' % (str(int(hours)).zfill(2), str(int(minutes % 60)).zfill(2), str(int(time_s % 60)).zfill(2))

def load_points_and_polygon(folder):
    """Loads all gpx files into a list of points"""
    print ("Loading files...")
    with open('polylines.js', 'w') as outputfile:
        outputfile.write('function addLines(map) {')
        with click.progressbar(os.listdir(folder)) as bar:
            for filename in bar:
                if filename.endswith(".gpx"):
                    gpx_file = open(f'{folder}/' + filename)
                    try:
                        color='#3388ff'
                        gpx = gpxpy.parse(gpx_file)
                        if gpx.time < datetime.datetime(2019, 8, 1, 0, 0, 0, 0, datetime.timezone.utc):
                            gpx_file.close()
                            os.rename(f'{folder}/' + filename, f'{folder}/archive/' + filename)
                        else:
                            tooltip = filename + ' - ' + gpx.time.strftime('%x')
                            polygon="L.polyline(["
                            for track in gpx.tracks:
                                if track.name:
                                    tooltip += ' - ' + track.name #+ ' (' + track.type + ')'
                                    try:
                                        moving_data = track.get_moving_data()
                                        if moving_data:
                                           tooltip += ' - duration:' + format_time(moving_data.moving_time)
                                    except :
                                        pass
                                    if track.type == 'Ride' or track.type == '1':
                                       color='#ff22ff'
                                for segment in track.segments:
                                    for point in segment.points:
                                        polygon += "["+str(point.latitude)+","+str(point.longitude)+"],"
                            polygon = polygon[:-1] + "],{color:'" + color + "',weight:2}).bindTooltip('" + html.escape(tooltip) + "').on('mouseover',function(e){e.target.setStyle({color:'red'});}).on('mouseout',function(e){e.target.setStyle({color:'" + color + "'});}).addTo(map);"
                            outputfile.write(polygon)
                    except :
                       print (f"Failed to load {filename} : ", sys.exc_info()[0])

        outputfile.write('}')
    print ("Done...")




if __name__ == '__main__':
    main()
