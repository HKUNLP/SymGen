#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyswip import Prolog

prolog = Prolog()
prolog.consult("geobase.pl")
prolog.consult("geoquery.pl")
# print(list(prolog.query("compile('geobase.pl'),compile('geoquery.pl'),use_module(library(time)),catch((call_with_time_limit(5, execute_query(answer(A,count(A,(state(A),loc(B,A),lower(B,C),lowest(C,(place(C),loc(C,D),const(D,stateid(alabama))))))), U01)), call_with_time_limit(5, execute_query(answer(A,count(B,(state(B),low_point(B,C),lower(C,D),low_point(E,D),const(E,stateid(alabama))),A)), U02)), print(0), (U01 == U02 -> print(' y') ; print(' n')), nl), time_limit_exceeded, (print(0), print(' n'), nl))")))
a = list(prolog.query("execute_query(answer(A,next_to(A,B),const(B,stateid(utah))), Ans)"))
# a = list(prolog.query("execute_query(answer(A,largest(B,(state(A),population(A,B)))), Ans1),execute_query(answer(A,largest(B,(state(A),population(A,B)))), Ans2)", maxresult=1))
# print([i.value for i in a[0]['Ans1']] == [i.value for i in a[0]['Ans2']])
print([i.value for i in a[0]['Ans']])
print(a)
# print(list(prolog.query("execute_query(answer(A,count(A,(state(A),loc(B,A),lower(B,C),lowest(C,(place(C),loc(C,D),const(D,stateid(alabama))))))), U)", maxresult=1)))

