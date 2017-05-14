# -*- coding: utf-8 -*-


def format_timestamp(timestamp):
    """Format a seconds timestamp for output in the form hh:mm:ss."""
    total_seconds = round(timestamp)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)
