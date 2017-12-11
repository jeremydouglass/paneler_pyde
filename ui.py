"""Simple user interface text boxes and buttons."""

from __future__ import print_function

# pylint: disable=invalid-name

class TextList(object):
    """A simple text box."""
    def __init__(self, text_list, x, y, w, h, margin=2, title=''):
        self.text_list = text_list
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.m = margin
        self.title = title

    def __repr__(self):
        return "TextList({}, {}, {}, {}, margin={}, title='{}')".format(
            self.text_list, self.x, self.y, self.h, self.m, self.title)

    def display(self):
        """Draw to screen."""
        m = self.m
        x = self.x + m
        y = self.y + m
        w = self.w - (2*m)
        h = self.h - (2*m)
        if self.title:
            with pushStyle():
                ## title box
                fill(220, 220, 255)
                stroke(64)
                rect(x, y, w, 24)
                ## title text
                fill(0)
                textSize(16)
                textLeading(12)
                textAlign(CENTER)
                text(self.title, x, y, w, 20)
            ## adjust remaining content area
            y = y+24
            h = h-24
        with pushStyle():
            fill(255)
            rect(x, y, w, h)
            fill(0)
            textSize(10)
            textLeading(10)
            textAlign(LEFT)
            if callable(self.text_list):
                txt = '\n'.join(self.text_list())
            elif isinstance(self.text_list, list):
                txt = '\n'.join(self.text_list())
            else:
                txt = self.text_list
            text(txt, x+m, y+m, w-2*m, h-2*m)

    def collide(self, px, py):
        """Point-rectangle collision detection."""
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h

class Button(object):
    """A simple button."""

    def __init__(self, label, x, y, w, h, click_duration=30,
                 callback='', call='', info='', margin=2):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.click_duration = click_duration
        self.callback = callback
        self.call = call
        self.info = info
        self.m = margin

        self.is_over = False
        self.click_time = 0

        self.strokecolor = color(64)
        self.strokeweight = 1
        self.bgcolor = color(207, 221, 236)
        self.bgcolor_over = color(207, 207, 255)
        self.bgcolor_click = color(255, 221, 207)
        self.labelcolor = color(0)
        self.labelsize = 10
        self.textcolor = color(0)
        self.textsize = 14

    def display(self):
        """Draw to screen."""
        m = self.m
        x = self.x + m
        y = self.y + m
        w = self.w - 2*m
        h = self.h - 2*m
        if self.click_time > 0:
            self.click_time -= 1
        with pushStyle():
            textSize(self.textsize)
            stroke(self.strokecolor)
            strokeWeight(self.strokeweight)
            if self.click_time != 0:
                fill(self.bgcolor_click)
            elif self.is_over:
                fill(self.bgcolor_over)
            else:
                fill(self.bgcolor)
            rect(x, y, w, h)
            fill(0)
            textAlign(CENTER, CENTER)
            if self.info:
                text(self.label, x + (w / 2), y + (h / 2) - 5)
                textSize(self.labelsize)
                text(self.info, x + (w / 2), y + (h / 2) + 10)
            else:
                text(self.label, x + (w / 2), y + (h / 2))

    def click(self, px, py):
        """Perform click actions if the point over the object."""
        if self.collide(px, py):
            if self.click_time == 0:
                ## start timer for click display
                self.click_time = self.click_duration
                if self.call == 'selectInput':
                    print('Select a data file:')
                    selectInput("Select a data file:", self.callback)
                elif self.call == 'selectFolder':
                    print('Select a data file:')
                    selectFolder("Select a data file:", self.callback)
                else:
                    if callable(self.callback):
                        self.callback()
        return self.click_time

    def over(self, px, py):
        """Perform hover actions if the point over the object."""
        if self.collide(px, py):
            if self.click_time == 0:
                self.is_over = True
        else:
            if self.click_time == 0:
                self.is_over = False
        return self.is_over

    def collide(self, px, py):
        """Point-rectangle collision detection."""
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h

    def no_change(self):
        """Hide click and hover changing color behavior."""
        self.bgcolor_click = self.bgcolor_over = self.bgcolor
