import search
import random
import math
import itertools

ids = ["111111111", "222222222"]


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.impass, self.gass_station = self.init_map(initial['map'])
        self.taxies_name = ()
        self.cap_s = []
        self.taxi= self.init_taxis(initial)
        self.p_tuole= self.init_passengers(initial)
        self.num_taxi=len(self.taxi)
        self.size_map = (len(initial['map'][0]),len(initial['map'][1]))
        start_state=(self.taxi,self.p_tuole)
        search.Problem.__init__(self, start_state)

    def init_map(self, initial):
        gass_station = ()
        impass = ()
        row = len(initial)
        col = len(initial[1])
        size_map = (row, col)
        for i in range(row):
            for j in range(col):
                if initial[i][j] == 'G':
                    gass_station = gass_station + ((i, j),)
                if initial[i][j] == 'I':
                    impass = impass + ((i, j),)
        return impass, gass_station

    def init_taxis(self, initial):
        t_dict = initial['taxis']
        taxi = ()
        n_taxi = len(t_dict.keys())
        for t_name in t_dict.keys():
            self.taxies_name += (t_name,)
            self.cap_s.append(t_dict[t_name]['capacity'])
            if n_taxi == 1:
                taxi = ((t_name, t_dict[t_name]['location'], t_dict[t_name]['capacity'], t_dict[t_name]['fuel'], ()),)
            if n_taxi != 1:
                taxi_toadd = (
                (t_name, t_dict[t_name]['location'], t_dict[t_name]['capacity'], t_dict[t_name]['fuel'], ()),)
                taxi = taxi + taxi_toadd
        return taxi

    def init_passengers(self, initial):
        p_dict = initial['passengers']
        p = ()
        n_p = len(p_dict.keys())
        for p_name in p_dict.keys():
            # (name,loc,dest)
            if n_p == 1:
                p = ((p_name, p_dict[p_name]['location'], p_dict[p_name]['destination']),)
            if n_p != 1:
                p_toadd = ((p_name, p_dict[p_name]['location'], p_dict[p_name]['destination']),)
                p = p + p_toadd
        return p

    def in_bound(self, row, col, options):
        # moves=["move up","move down","move right","move left"]
        if row < self.size_map[0] -1:
            options[1] = (row+1, col)  # down
        if row > 0:
            options[0] = (row-1, col)  # up
        if col < self.size_map[1] -1:
            options[2] = (row, col+1)  # right
        if col > 0:
            options[3] = (row, col-1)  # left

    def dest_check(self, comb, taxi_c_loc, com):
        for i, ac in enumerate(comb):
            loc_set = ()
            if ac[0] in com:
                loc_set += taxi_c_loc[i]
            if ac[0] == 'move' and ac[2] in loc_set:
                return False
            if ac[0] == 'move':
                loc_set += ac[2]
        return True

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        moves = ["move up", "move down", "move right", "move left"]
        com = ('pick up', 'drop off', 'wait', 'refuel')
        taxis_places = []
        taxi_c_loc = []
        taxi_tup = state[0]
        actions_set = ()
        s_p_array = [[6, 5, 4, 3, 2], [7, 'I', 3, 2, 1], [8, 9, 'I', 3, 2],[ 9, 10, 11, 'I', 3]]
        for i, t in enumerate(taxi_tup):
            taxis_places.append(())
            taxi_c_loc.append(t[1])
        for index, t in enumerate(taxi_tup):
            temp_texi = ()
            loc = t[1]
            options = [0, 0, 0, 0]
            if t[3] != 0:
                self.in_bound(loc[0], loc[1], options)

                for place in options:
                    if place != 0:
                        if place not in self.impass:
                            temp_texi += ((place),)
                for i in temp_texi:
                    taxis_places[index] += (('move', t[0], i),)

        # pickup
        pasenger_tup = state[1]
        for p in pasenger_tup:
            for index, t in enumerate(taxi_tup):
                if t[1] == p[1] and t[2] - 1 >= 0:
                    taxis_places[index] += (('pick up', t[0], p[0]),)

        # dropoff
        for p in pasenger_tup:
            for index, t in enumerate(taxi_tup):
                if t[1] == p[2] and t[0] == p[1]:
                    taxis_places[index] += (('drop off', t[0], p[0]),)

        # wait+fuell
        for index, t in enumerate(taxi_tup):
            if (t[1] in self.gass_station):
                taxis_places[index] += (('refuel', t[0]),)
            taxis_places[index] += (('wait', t[0]),)

        for comb in itertools.product(*taxis_places):
            if self.dest_check(comb, taxi_c_loc, com):
                actions_set += (comb,)
        return actions_set

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        act_arry = ['move', 'pick up', 'drop off', 'wait', 'refuel']
        update_taxi_s = ()
        update_pass_s = ()
        update_pass_sf = ()
        taxi_tup = state[0]
        pass_tup = state[1]

        for i, act in enumerate(action):
            cur_taxi = taxi_tup[i]
            # check if action is move
            if act[0] == act_arry[0]:
                update_taxi_s += ((cur_taxi[0], act[2], cur_taxi[2], cur_taxi[3] - 1),)
            # check if action is wait
            if act[0] == act_arry[3]:
                update_taxi_s += ((cur_taxi[0], cur_taxi[1], cur_taxi[2], cur_taxi[3]),)
            # check if action is pickup
            if act[0] == act_arry[1]:
                for p in pass_tup:
                    # check with passenger need to be picked up
                    if act[2] == p[0]:
                        # taxi current passenger group and capacity update
                        update_taxi_s += ((cur_taxi[0], cur_taxi[1], cur_taxi[2] - 1, cur_taxi[3]),)
                        # pass location is update to taxi that picked him up
                        update_pass_s += ((p[0], cur_taxi[0], p[2]),)
                # check if action is dropoff
            # ('taxi 1', (3, 3), 2, 15, (('Moshe', (3, 1), (0, 0)),))
            if act[0] == act_arry[2]:
                for p in pass_tup:
                    if act[2] == p[0]:
                        update_pass_s += ((p[0], 'goodbye', p[1]),)
                        update_taxi_s += ((cur_taxi[0], cur_taxi[1], cur_taxi[2] + 1, cur_taxi[3]),)
            ##check if action is refuel
            if act[0] == act_arry[4]:
                temp_fuel=0
                for taxi_fuel in self.taxi:
                    if cur_taxi[0]==taxi_fuel[0]:
                        temp_fuel=taxi_fuel[3]
                update_taxi_s += ((cur_taxi[0], cur_taxi[1], cur_taxi[2], temp_fuel),)

        pass_names_updated = ()
        for p in update_pass_s:
            pass_names_updated += (p[0],)
            if p[1] != 'goodbye':
                update_pass_sf += (p,)
        for p in pass_tup:
            if p[0] not in pass_names_updated:
                update_pass_sf += (p,)
        return (update_taxi_s, update_pass_sf)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        if len(state[1]) == 0:
            return True
        else:
            return False

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return  1.2*self.h_1(node) + 0.1*self.h_fuel(node)+ 0.95*self.h_2(node)+0.95*self.h_2_new(node) +0.07*self.h_min_dis(node)

    def h_1(self, node):
        """
        This is a simple heuristic
        """
        passe = node.state[1]
        counter = 0
        unpicked_count = 0
        taxi = ()
        taxi_nb = len(node.state[0])
        cap_sum=0

        for c in self.cap_s:
            cap_sum += c
        for p in passe:
            #change to taxi 1/taxi2
            if p[1] in self.taxies_name:
                counter += 1
            else:
                unpicked_count += 1
        return (unpicked_count*2 + counter) / taxi_nb

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        d = 0
        pas = node.state[1]
        for p in pas:
            if p[1] not in self.taxies_name:
                d += self.manhattan_dist(p[1], p[2])
            else:
                for t in node.state[0]:
                    if p[1] == t[0]:
                        d += self.manhattan_dist(t[1], p[2])
        return d / (len(node.state[0]))

    def h_fuel(self, node):
        taxi_state = node.state[0]
        flag = 0
        flag2 = 0
        d = 0
        cap_sum = 0
        for c in self.cap_s:
            cap_sum += c
        for t in taxi_state:
            for g in self.gass_station:
                p_t_fuel = self.manhattan_dist(t[1], g)
                d += p_t_fuel
                if t[3] < (p_t_fuel + 1) and len(node.state[1]) > 1:
                    flag = 1
                    if t[3] < 2:
                        for p in node.state[1]:
                            if t[0] == p[1] and t[3] == 0:
                                flag2 = 9999
                            else:
                                flag2 = 20
        h_1_val = (self.h_1(node) * len(node.state[0])*flag + 5 * (flag * d) + flag2) / (cap_sum +1)

        return h_1_val

    def h_2_new(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        d = 0
        pas = node.state[1]
        cap_sum = 0
        for c in self.cap_s:
            cap_sum += c
        for p in pas:
            if p[1] not in self.taxies_name:
                d += self.manhattan_dist(p[1], p[2])
            else:
                for t in node.state[0]:
                    if p[1] == t[0]:
                        d += self.manhattan_dist(t[1], p[2])
        return d / cap_sum

    def h_min_dis(self, node):
        min_array = []
        min_array_on_t = []
        flag = 0
        temp_min = 0
        sum_min = 0
        sum_on_t = 0
        for taxi in node.state[0]:
            for i, p in enumerate(node.state[1]):
                if p[1] not in self.taxies_name:
                    val = self.manhattan_dist(taxi[1], p[1])
                    if flag == 0:
                        min_array.append(val)
                        temp_min = val
                        flag == 1
                    elif val < temp_min:
                        min_array[i] = val
        for p in node.state[1]:
            if p[1] in self.taxies_name:
                for t in node.state[0]:
                    if t[0] == p[1]:
                        min_array_on_t.append(self.manhattan_dist(t[1], p[2]))
        for i in min_array:
            sum_min += i
        for i in min_array_on_t:
            sum_on_t += i
        return sum_min*0.9+sum_on_t*0.1

    def manhattan_dist(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)

