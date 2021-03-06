#!/usr/bin/python
# -*- coding: utf-8 -*-

from spnotify import *
from nose.tools import *
import datetime


def test_Rule():

    contact_pattern = u'^(john|bob)$'
    ts = TimeSlots()
    ts.add(u'[12h00;13h35][23h00;23h59]')
    name = u'john'
    service_desc_regex = u'^disk space$'
    service_desc = u'disk space'
    hostname = u'srv-2'
    now = datetime.time(23, 2)
    weekdays = Weekdays(u'*')

    def test():
        rule = Rule(
            contact_names = Regexp(contact_pattern),
            hostnames = Regexp(u'^srv-'), timeslots = ts,
            weekdays=weekdays, service_desc = Regexp(service_desc_regex),
        )
        contact = Contact(
            name = name, sms_threshold = 4, rarefaction_threshold = 15,
            sms_url = u'http://hostname/sendsms.pl',
            email = u'john@domain.tld', phone_number=u'0666666666')
        notif = Notification(
            contact = contact, hostname = hostname, address = u'172.31.0.1',
            ntype = u'Problem', state = u'CRITICAL', business_impact = 4,
            additional_info = u'CRITICAL, there is a big problem',
            number = 7, service_desc = service_desc, time = now)
        return rule.is_matching_with(notif)

    assert_true(test())

    current_weekday = datetime.datetime.now().isoweekday()
    days_without_current_day = [1, 2, 3, 4, 5, 6, 7]
    days_without_current_day.remove(current_weekday)

    weekdays = Weekdays(unicode(days_without_current_day)) # weekday doesn't match
    assert_false(test())

    days_with_current_day = unicode(list(set([current_weekday, 1, 2])))
    weekdays = Weekdays(days_with_current_day) # weekday matches
    assert_true(test())

    now = datetime.time(0, 0) # time doesn't match
    assert_false(test())

    now = datetime.time(23, 0)
    hostname = u'wsrv-2' # hostname doesn't match
    assert_false(test())

    contact_pattern = u'!^(john|bob)$'
    hostname = u'srv-2'
    name = u'bobby' # name doesn't match but the pattern begins with '!'
    assert_true(test())

    name = u'bob' # name matches but the pattern begins with '!'
    assert_false(test())

    name = u'pit' # it's matched (it's host notification)
    service_desc_regex = u''
    service_desc = None
    assert_true(test())

    name = u'john'
    service_desc_regex = u'cpu'
    service_desc = None
    assert_false(test())


def test_Regexp():

    r1 = Regexp(u'^(aaa|bbb)')
    r2 = Regexp(u'!^(aaa|bbb)') # '!' must reverse the regex.
    r3 = Regexp(u'') # an empty regex must catch nothing.
    assert_false(r1.is_empty())
    assert_true(r3.is_empty())
    assert_true(r1.catch(u'aaaxxxx'))
    assert_false(r1.catch(u'xaaaxxxx'))
    assert_true(r2.catch(u'xaaaxxxx'))
    assert_false(r2.catch(u'aaaxxxx'))
    assert_false(r3.catch(u''))
    assert_false(r3.catch(u'any'))


def test_Notification():

    c = Contact(
       name=u'john', sms_threshold=4, rarefaction_threshold=10,
       sms_url = u'http://hostname/sendsms.pl',
       email=u'john@domain.tld', phone_number=u'0666666666')
    notif = Notification(
        contact=c, hostname=u'google', address=u'www.google.fr',
        ntype=u'PROBLEM', state=u'CRITICAL', business_impact=4,
        additional_info=u'http is out!', number=34, service_desc=u'http')


def test_Contact():

    c = Contact(name=u'john', sms_threshold=4, rarefaction_threshold=10,
                sms_url = u'http://hostname/sendsms.pl',
                email=u'john@domain.tld', phone_number=u'0666666666')


def test_TimeSlot():

    t1 = datetime.time(14, 30)
    t2 = datetime.time(17, 47)
    ts = TimeSlot(t1, t2)
    t_in = datetime.time(14, 30)
    t_out = datetime.time(14, 29)
    assert_true(t_in in ts)
    assert_false(t_out in ts)


def test_TimeSlots():

    ta = datetime.time(20,4)
    tb = datetime.time(23,31)

    a1 = datetime.time(14, 30)
    a2 = datetime.time(17, 47)
    tsa = TimeSlot(a1, a2)

    b1 = datetime.time(19, 31)
    b2 = datetime.time(20, 9)
    tsb = TimeSlot(b1, b2)

    timeslots = TimeSlots()
    assert_false(ta in timeslots)

    timeslots = TimeSlots([tsa])
    assert_false(ta in timeslots)

    timeslots.add(tsb)
    assert_true(ta in timeslots)
    assert_false(tb in timeslots)

    timeslots.add(u'[9h35; 10h30] [23h25; 23h31]')
    assert_true(ta in timeslots)
    assert_true(tb in timeslots)

    timeslots2 = TimeSlots()
    timeslots2.add(u'[22h35;+1h07]')
    assert_true(str(timeslots2) == '[[22:35-->23:42]]')

    timeslots3 = TimeSlots()
    timeslots3.add(u'[23h57;+02h07]')
    assert_true(str(timeslots3) == '[[23:57-->23:59], [00:00-->02:04]]')
    c1 = datetime.time(0, 59)
    c2 = datetime.time(2, 6)
    assert_true(c1 in timeslots3)
    assert_false(c2 in timeslots3)

    timeslots4 = TimeSlots()
    timeslots4.add(u'[22h35;+23h59]')
    assert_true(str(timeslots4) == '[[22:35-->23:59], [00:00-->22:34]]')

    timeslots5 = TimeSlots()
    timeslots5.add(u'[22h35;23h07]')
    assert_true(str(timeslots5) == '[[22:35-->23:07]]')


def test_Line():

    l = Line(u'    aaaa bbbb # just a test...   ')
    assert_equal(l.line, u'aaaa bbbb')
    l = Line(u'    aaaa bbbb')
    assert_equal(l.line, u'aaaa bbbb')
    l = Line(u'# blabla')
    assert_equal(l.line, u'')
    l = Line(u'')
    assert_equal(l.line, u'')

    l = Line(u'^john:^srv-$:load cpu:[00h30;2h00][14h00;17h00]:*')
    rule = l.get_rule()
    assert_true(isinstance(rule, Rule))
    l = Line(u'^john:^srv-$:load cpu:::[00h30;2h00][14h00;17h00]:*') # bad syntax
    rule = l.get_rule()
    assert_true(rule is None)





