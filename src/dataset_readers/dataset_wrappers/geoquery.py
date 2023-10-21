from src.utils.misc import App
from src.dataset_readers.dataset_wrappers.base_dsw import ABC

field_getter = App()

sk_prompt = '''%geobase.pl
:- ensure_loaded(library('lists')).
:- ensure_loaded(library('ordsets')).
:- ensure_loaded(geobase).

country(countryid(usa)).

state(stateid(State)) :- state(State,_,_,_,_,_,_,_,_,_).

city(cityid(City,St)) :- city(_,St,City,_).

river(riverid(R)) :- river(R,_,_). 

lake(lakeid(R)) :- lake(R,_,_). 

mountain(mountainid(M)) :- mountain(_,_,M,_). 

place(placeid(P)) :- highlow(_,_,P,_,_,_).
place(placeid(P)) :- highlow(_,_,_,_,P,_).

abbreviation(stateid(State), Ab) :- state(State,Ab,_,_,_,_,_,_,_,_).
abbreviation(Ab) :- abbreviation(_,Ab).

capital(stateid(State), cityid(Cap,St)) :- state(State,St,Cap,_,_,_,_,_,_,_).
capital(Cap) :- capital(_,Cap).

loc(X,countryid(usa)) :- city(X) ; state(X) ; river(X) ; place(X) ; lake(X); mountain(X).
loc(cityid(City,St), stateid(State)) :- city(State, St, City,_).
loc(cityid(City,St), stateid(State)) :- state(State,St,City,_,_,_,_,_,_,_).
loc(placeid(P), stateid(S)) :- highlow(S,_,P,_,_,_).
loc(placeid(P), stateid(S)) :- highlow(S,_,_,_,P,_).
loc(mountainid(P), stateid(S)) :- mountain(S,_,P,_).
loc(riverid(R), stateid(S)) :- river(R,_,States), member(S,States).
loc(lakeid(L),stateid(S)) :- lake(L,_,States), member(S,States).

traverse(riverid(R), stateid(S)) :- river(R,_,States), member(S,States).
traverse(riverid(R), countryid(usa)). 

high_point(countryid(usa), placeid('mount mckinley')).
high_point(stateid(S), placeid(P)) :- highlow(S,_,P,_,_,_).

low_point(countryid(usa), placeid('death valley')).
low_point(stateid(S), placeid(P)) :- highlow(S,_,_,_,P,_).

area(stateid(X),Areal) :- state(X,_,_,_,Area,_,_,_,_,_), Areal is float(Area).
area(countryid(X),Areal) :- country(X,_,Area), Areal is float(Area).

major(cityid(C,S)) :- X = cityid(C,S), city(X), population(X,P), P > 150000.
major(riverid(R)) :- X = riverid(R), river(X), len(X,L), L > 750.

first(G) :- (G -> true).

n_solutions(N,Goal) :- findall(Goal, Goal, GList0), length(Solutions, N), append(Solutions,_,GList0), member(Goal, Solutions).

nth_solution(N,Goal) :- findall(Goal, Goal, GList), nth(N,GList,Goal).

population(countryid(X),Pop) :- country(X,Pop,_).
population(stateid(X),Pop) :- state(X,_,_,Pop,_,_,_,_,_,_).
population(cityid(X,St), Pop) :- city(_,St,X,Pop).

len(riverid(R), L) :- river(R,L,_).

elevation(placeid(P),E) :- highlow(_,_,_,_,P,E).
elevation(placeid(P),E) :- highlow(_,_,P,E,_,_).
elevation(mountainid(P),E) :- mountain(_,_,P,E).

size(stateid(X), S) :- area(stateid(X), S).
size(cityid(X,St), S) :- population(cityid(X,St), S).
size(riverid(X), S) :- len(riverid(X),S).
size(placeid(X), S) :- elevation(placeid(X),S).
size(X,X) :- number(X).

next_to(stateid(X),stateid(Y)) :- border(X,_,Ys), member(Y,Ys).

density(S,D) :- population(S,P), area(S,A), D is P / A.

largest(Var, Goal) :- findall(Size-Goal, (Goal,size(Var,Size)), Pairs0), max_key(Pairs0, Goal).

smallest(Var, Goal) :- findall(Size-Goal, (Goal,size(Var,Size)), Pairs0), min_key(Pairs0, Goal).

count(V,Goal,N) :- findall(V,Goal,Ts), sort(Ts, Unique), length(Unique, N).

at_least(Min,V,Goal) :- count(V,N,Goal), Goal, N >= Min.

at_most(Max,V,Goal) :- count(V,Goal,N), N =< Max.

answer(Var, Goal) :-  nl,nl, findall(Name,(Goal,print_name(Var,Name)),Answers), sort(Answers,Unique), format('Answer = ~w~n',[Unique]).
'''


@field_getter.add("q")
def get_q(entry):
    return f"%Natural Language: {entry['nl']}"


@field_getter.add("search_q")
def get_search_q(entry):
    return entry['nl']


@field_getter.add("a")
def get_a(entry):
    return entry['prolog']


@field_getter.add("qa")
def get_qa(entry):
    # in-context example for few-shot generating answer
    # return f"%Natural Language: {entry['nl']}\n{entry['prolog']}"
    return f"%Natural Language: {entry['nl']}\n{entry['prolog']}"


@field_getter.add("gen_q")
def get_gen_q_instruction(entry):
    prompt = "{sk_prompt}%Translate the natural language description to prolog commands.\n\n" \
             "{ice_prompt}%Natural Language: "
    return prompt.format(sk_prompt=sk_prompt, ice_prompt='{ice_prompt}')


@field_getter.add("gen_a")
def get_gen_a_instruction(entry):
    prompt = "{sk_prompt}%Translate the natural language description to prolog commands.\n\n" \
             "{ice_prompt}%Natural Language: {question}\nanswer("
    # prompt = "{sk_prompt}\n\n" \
    #          "{ice_prompt}{question}\nanswer("
    prompt = prompt.format(sk_prompt=sk_prompt, question=entry['nl'], ice_prompt='{ice_prompt}')
    # prompt = prompt.format(sk_prompt='', question=entry['nl'], ice_prompt='{ice_prompt}')
    return prompt


class DatasetWrapper(ABC):
    name = "geoquery"
    question_field = "nl"
    answer_field = "prolog"
    hf_dataset = ''
    hf_dataset_name = ''
    field_getter = field_getter
