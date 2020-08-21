#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 19:44:32 2020

@author: sofiat
"""

from readinput import READSPAST



class SuperPoly:
    def __init__(self, filename):

        self.filename = filename
        r = READSPAST(self.filename)
        r.read_file()

        self.students = r.students
        self.projects = r.projects
        self.lecturers = r.lecturers

        self.sp = r.sp # student preference information
        self.sp_copy = r.sp_copy
        self.sp_no_tie = r.sp_no_tie
        self.sp_no_tie_deletions = r.sp_no_tie_deletions
        self.plc = r.plc # project information
        self.lp = r.lp # lecturer preference information
        self.lp_copy = r.lp_copy
        
        # -------------------------------------------------------------------------------------------------------------------
        self.unassigned = [] # keeps track of unassigned students
        self.su_M = {}
        self.M = {} #provisional assignment graph
        for student in r.sp:
            self.unassigned.append(student)
            self.M[student] = set() # set of p_j's adjacent to s_i
        for project in r.plc:
            self.M[project] = [set(), r.plc[project][1]] # [students assigned to p_j, remnant of c_j] 
        for lecturer in r.lp_copy:
            self.M[lecturer] = [set(), set(), r.lp_copy[lecturer][0]] # [students assigned to l_k, non-empty p_j's in G offered by l_k, remnant of d_k]

        self.full_projects = set()

        self.run_algorithm = True
        self.blocking_pair = False
        self.found_susm = 'N'
        self.restart_extra_deletions = False
        
        
    # =======================================================================
    # add pair (s_i, p_j) to M
    # =======================================================================    
    def add_edge_to_M(self, student, project, lecturer):
        
        self.M[student].add(project) 
        
        self.M[project][0].add(student)
        self.M[project][1] -= 1  # reduce c_j
        
        #self.M[lecturer][0].add(student)        
        self.M[lecturer][1].add(project)        
        if student not in self.M[lecturer][0]:
            self.M[lecturer][0].add(student)
            self.M[lecturer][2] -= 1  # reduce d_k
             
    
    
    # =======================================================================
    # remove pair (s_i, p_j) from M
    # =======================================================================       
    def remove_edge_from_M(self, student, project, lecturer):
        if project in self.M[student]:
            self.M[student].remove(project) 
            
            self.M[project][0].remove(student)
            self.M[project][1] += 1  # increment c_j   
            
            # if the project becomes an isolated vertex
            if self.M[project][0] == set():
                self.M[lecturer][1].remove(project)
            
            # if in M, student no longer has any project in common w/ lecturer
            if student in self.M[lecturer][0] and self.M[student].intersection(self.M[lecturer][1]) == set():
                self.M[lecturer][0].remove(student)
                self.M[lecturer][2] += 1  # increment d_k
                # if full(l_k) was previously True, and l_k becomes undersubscribed here, we do not set it back to False
                # Lemma 6 of the paper will kick in if the lecturer did not fill up at the termination of the algorithm
                
#                 if d_k > 0, set full(d_k) to False
                #if self.M[lecturer][2] > 0:
                    #self.lp[lecturer][3] = False
    
    
    # =======================================================================
    # delete (s_i, p_j) from A(s_i)   ---! and not L_k^j
    # =======================================================================
    def delete(self, student, project, lecturer):       
        # replace project with dp in the student's preference list
        # also remove it from sp_no_tie_deletions
        if project in self.sp_no_tie_deletions[student]:
            # get the rank of pj on the student's list, say (2, 0)
            # 2 is the position of p_j's tie T in A(s_i)
            # and 0 is the position of p_j in T
            p_rank = self.sp[student][2][project]
            self.sp[student][1][p_rank[0]][p_rank[1]] = 'dp'  # we replace the project in this position by a dummy project
            self.sp_no_tie_deletions[student].remove(project)
            self.plc[project][3].append(student)  # keep track of students who were rejected from pj
        
        # remove the pair from M
        self.remove_edge_from_M(student, project, lecturer)
            
        # if student is not paired with a project in M and has a non-empty list
        # add her to the list of unassigned students
        if self.M[student] == set() and student not in self.unassigned and len(self.sp_no_tie_deletions[student]) > 0:
#            print(self.M[student], student, project)
            self.unassigned.append(student) 
    
    # =======================================================================
    # find strict successors students in L_k^j
    # =======================================================================    
    def p_strict_successors(self, project):
        """
        param: p_j
        return: starting index of strict successors in Lkj as well as the students,
        or None, [] if pj has no strict successors.
        """
        lecturer = self.plc[project][0]
        cj = self.plc[project][1]
        Lkj_students = self.lp[lecturer][2][project]  # students who chose p_j according to Lk
        Lkj_tail_index = self.plc[project][4]
        Mpj = self.M[project][0]
        successor_index = None
        successor_students = []
        count = 0
        for i in range(Lkj_tail_index+1):
            assigneees = Mpj.intersection(Lkj_students[i])
            count += len(assigneees)
            if count == cj and i < Lkj_tail_index: 
                # second part of if statement takes care of scenario where pj has no strict successors
                successor_index = i+1
                self.plc[project][4] = i # pointer to index of new tail
            
            # successor_index could be None if pj is full and Lkj_tail_index is pointing to the worst tie
            # i.e., if pj has no strict successors         
            if successor_index != None:
                successor_students = Lkj_students[successor_index:]
                break
            
#        print('L_k_j dominated index is: ', dominated_index)
#        print('L_k_j dominated student is: ', dominated_students)
        return successor_index, successor_students


    # =======================================================================
    # find strict successors students in L_k
    # =======================================================================    
    def l_strict_successors(self, lecturer):
        """
        param: l_k
        return: starting index of strict successors in Lk as well as the students,
        or None, [] if lk has no strict successors.
        """
        
        dk = self.lp[lecturer][0]
        Lk_students = self.lp[lecturer][1]  # students who chose some project offered by lk
        Lk_tail_index = self.lp[lecturer][4] # should this index be 5? ****
        Mlk = self.M[lecturer][0]
        successor_index = None
        successor_students = []
        count = 0
        for i in range(Lk_tail_index+1):
            assigneees = Mlk.intersection(Lk_students[i])
            count += len(assigneees)
            #print(pj, Lk_students[i], count)
            if count == dk and i < Lk_tail_index:
                successor_index = i+1
                self.lp[lecturer][4] = i
            # we are guaranteed that successor_index will not be None at some point
            # because we only find l_strict_successors when lk becomes full
            # also pointer to index of tail should ONLY be updated when lecturer is full
            if successor_index != None:
                successor_students = Lk_students[successor_index:]
                break
    
#        print('L_k dominated index is: ', dominated_index)
#        print('L_k dominated student is: ', dominated_students)
        return successor_index, successor_students  
    
    # =======================================================================
    # while loop that constructs M from students preference lists
    # =======================================================================    
    def while_loop(self):
        while self.unassigned:         
            
            student = self.unassigned.pop(0)  
#            print('current student', student)
            s_preference = self.sp[student][1]  # the projected preference list for this student.. this changes during the allocation process.
            # self.sp[student][3] points to the tie at the head of s_i's list 
            # if tie pointer is not up to length of pref list --- length is not 0-based!
            head_index = self.sp[student][3] # 0-based
            pref_list_length = self.sp[student][0] # !0-based
#            print('unassigned', self.unassigned, student, s_preference[self.sp[student][3]])
            if head_index < pref_list_length:
                tie = s_preference[head_index] # projects at the head of the list ::: could be length 1 or more
                self.sp[student][3] += 1  # we increment head_index pointer --> moves inward by 1 
#                print(tie)
                for project in tie:
                    if project == 'dp':
                        continue
                    else:                        
                        lecturer = self.plc[project][0]
                        # add the edge (student, project) to M
                        self.add_edge_to_M(student, project, lecturer)
                        # ----------- if project is oversubscribed -----------
                        if self.M[project][1] < 0:
                            Lkj_students = self.lp[lecturer][2][project]
                            tail_index = self.plc[project][4] 
                            tail_students = Lkj_students[tail_index]
                            
                            self.plc[project][4] -= 1 
                            self.lp[lecturer][2][project] = self.lp[lecturer][2][project][:tail_index]
                            
                            for st in tail_students:
                                self.delete(st, project, lecturer)
                                #print('delete line 12', st, project)
                                
                        # ----------- if lecturer  is oversubscribed -----------
                        elif self.M[lecturer][2] < 0:
                            Lk_students = self.lp[lecturer][1]
                            tail_index = self.lp[lecturer][4] 
                            tail_students = Lk_students[tail_index]
                            #print(lecturer, tail_index, self.lp[lecturer], self.M[lecturer])
                            self.lp[lecturer][4] -= 1                            
                            self.lp[lecturer][1] = self.lp[lecturer][1][:tail_index]
                            
                            Pk = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                            for st in tail_students:
                                a_t = set(self.sp_no_tie_deletions[st])  # the student's altered preference list without ties..
                                common_projects = Pk.intersection(a_t)
                                for pu in common_projects:
                                    self.delete(st, pu, lecturer)
                                    #print('delete line 16', st, pu)
                            
                        # ----------- if project is full -----------
                        if self.M[project][1] == 0:  
                            self.plc[project][2] = True   # set full(p_j) to True     
                            successor_index, successor_students = self.p_strict_successors(project) # finds dominated students and the starting index on L_k^j
                            # we delete dominated students from L_k^j by replacing L_k_j with non-dominated students
                            if successor_index != None:
                                self.lp[lecturer][2][project] = self.lp[lecturer][2][project][:successor_index] 
                                #print('remaining L_k^j: ', self.lp[lecturer][2][project])
                                for tie in successor_students:
                                    for st in tie:
                                        self.delete(st, project, lecturer)                                    
                                        #print('delete line 21', st, project, self.M[project][0])
                                    
                        # ----------- if lecturer is full  -----------
                        if self.M[lecturer][2] == 0:
                            self.lp[lecturer][3] = True
                            successor_index, successor_students = self.l_strict_successors(lecturer) # finds dominated students and the starting index on l_k
                            #print(successor_index, successor_students, self.M)                         
                            # we delete dominated students from l_k by replacing l_k with non-dominated students
                            if successor_index != None: # otherwise, successor_index is None
                                self.lp[lecturer][1] = self.lp[lecturer][1][:successor_index]
                                Pk = set([i for i in self.lp[lecturer][2].keys()])  # all the projects that lecturer is offering
                                for tie in successor_students:
                                    for st in tie:
                                        a_t = set(self.sp_no_tie_deletions[st])  # the student's altered preference list without ties..
                                        common_projects = Pk.intersection(a_t)
                                        for pu in common_projects:
                                            self.delete(st, pu, lecturer)
    #                                        print('delete line 26', st, pu)
                            
            #########################################################################################################################################
            if self.M[student] != set() and student in self.unassigned:
                self.unassigned.remove(student)
            # !* if the current student is unassigned in the matching, with a non-empty preference list, we re-add the student to the unassigned list
            if self.M[student] == set() and student not in self.unassigned and len(self.sp_no_tie_deletions[student]) > 0:  #--- caught in an infinite while loop for tie-9 (check later!**)   
                self.unassigned.append(student)
            #########################################################################################################################################
    
    # =======================================================================
    # repeat until loop -- terminates when every unassigned student has an empty list
    # ======================================================================= 
    def outer_repeat(self):
        while self.unassigned or self.restart_extra_deletions:
            self.while_loop()                   
            # ** extra deletions (lines 27 - 34 of Algorithm SPA-ST-super)
            # the variable self.restart_extra_deletions takes care of instances where
            # an extra deletion does not restart the while loop; and at the same time,
            # more deletions needs to take place before the algorithm terminates
            self.restart_extra_deletions = False
            for pj in self.plc:
                #deleted_students = self.plc[pj][3]
                cj_remnant = self.M[pj][1]
                if cj_remnant > 0 and self.plc[pj][2]:  # pj is undersubscribed and full(pj) is True                 
                    lk = self.plc[pj][0] # lecturer who offers pj
                    sr = self.plc[pj][3][-1] # most preferred student rejected from pj
                    lk_tail_pointer = self.lp[lk][4]
                    Lk_students = self.lp[lk][1][:]
                    # is sr in any of the ties from Lk's tail inwards? 
                    # If yes, set found to True
                    found = False                    
                    while lk_tail_pointer >= 0:
                        if sr in Lk_students[lk_tail_pointer]:
                            found = True
                            if lk_tail_pointer < self.lp[lk][4]:
                                self.restart_extra_deletions = True
                            break
                        lk_tail_pointer -= 1
                        
                    if found:        
                        Lk_tail = Lk_students[-1] # copy the tail
                        self.lp[lk][1] = self.lp[lk][1][:-1] # delete the tail from Lk's preference list
                        self.lp[lk][4] -= 1 # decrement Lk's worst pointer 
                        Pk = set([i for i in self.lp[lk][2].keys()])  # all the projects that lk is offering
                        for st in Lk_tail:  
                            # print(pj, lk, st)
                            a_t = set(self.sp_no_tie_deletions[st])  # the student's altered preference list without ties..
                            common_projects = Pk.intersection(a_t)
                            for pu in common_projects:
                                self.delete(st, pu, lk)
                                #print('delete line 34', st, pu)
#                                print('line 29 delete', st, pu, lk)

    
     # =======================================================================    
    # blocking pair types
    # =======================================================================    
    def blockingpair_1bi(self, student, project, lecturer):
        #  project and lecturer capacity
        cj, dk = self.plc[project][1], self.lp[lecturer][0]
        # no of students assigned to project in M
        project_occupancy, lecturer_occupancy = len(self.M[project][0]), len(self.M[lecturer][0])
        #  project and lecturer are both under-subscribed
        if project_occupancy < cj and lecturer_occupancy < dk:
            return True
        return False
    
    def blockingpair_1bii(self, student, project, lecturer):
        # p_j is undersubscribed, l_k is full and either s_i \in M(l_k)
        # or l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
        cj, dk = self.plc[project][1], self.lp[lecturer][0]
        project_occupancy, lecturer_occupancy = len(self.M[project][0]), len(self.M[lecturer][0])
        
        #  project is undersubscribed and lecturer is full
        if project_occupancy < cj and lecturer_occupancy == dk:
            Mlk_students = self.M[lecturer][0]
            if student in Mlk_students:
                return True
            remaining_Lk = self.lp[lecturer][1][:]
            for tie in remaining_Lk:
                if student in tie:
                    return True                
        return False
    
    def blockingpair_1biii(self, student, project, lecturer):
        # p_j is full and l_k prefers s_i to the worst student in M(p_j) or is indifferent between them
        cj, project_occupancy = self.plc[project][1], len(self.M[project][0])
            
        if project_occupancy == cj:
            remaining_Lkj = self.lp[lecturer][2][project][:]
            for tie in remaining_Lkj:
                if student in tie:
                    return True
        return False

    # =======================================================================    
    # Is M super stable? Check for blocking pair
    # self.blocking_pair is set to True if blocking pair exists
    # =======================================================================
    def check_stability(self):        
        for student in self.sp:
            preferred_projects = []
            if self.M[student] == set():
                preferred_projects = self.sp_no_tie[student]
            else:
                matched_project = self.M[student].pop()
                self.M[student].add(matched_project)
                rank_matched_project = self.sp_copy[student][2][matched_project][0]
                A_si = self.sp_copy[student][1]
                preferred_projects = [s for tie in A_si[:rank_matched_project+1] for s in tie]
                #indifference = A_si[rank_matched_project][:] # deep copy the tie containing M(s_i)
                preferred_projects.remove(matched_project)
        
            for project in preferred_projects:
                lecturer = self.plc[project][0]
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1bi(student, project, lecturer)
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1bii(student, project, lecturer)
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1biii(student, project, lecturer)
                
                if self.blocking_pair:
#                    print(student, project, lecturer)
                    break
            
            if self.blocking_pair:
                # print(student, project, lecturer)
                break
 
    # =======================================================================    
    # Is a student mutiply assigned in M?
    # =======================================================================
    def student_checker(self):
        for student in self.sp:
            if len(self.M[student]) > 1:
                # print(student + ' is assigned to ' + str(len(self.M[student])) + ' projects.')
                return True
        return False
                

    # -------------------------------------------------------------------------------------------------------------------------------
    #   --------------------- 2 :::: A LECTURER WAS FULL at some point and subsequently ends up UNDER-SUBSCRIBED --------------
    # -------------------------------------------------------------------------------------------------------------------------------
    def lecturer_checker(self):
        for lecturer,value in self.lp.items():
            # replete lecturer is not full in M
            dk, lecturer_occupancy_inM = self.lp[lecturer][0], len(self.M[lecturer][0])                
            full_lk = value[3]
            if full_lk and lecturer_occupancy_inM < dk :
                # print('replete lecturer "{lk}" is not full in M'.format(lk=lecturer))
                return True
        return False


    # -------------------------------------------------------------------------------------------------------------------------------
    #   ----------- 3 :::: A PROJECT WAS REJECTED FROM A STUDENT at some point and subsequently p_j, l_k ends up UNDER-SUBSCRIBED --
    # -------------------------------------------------------------------------------------------------------------------------------
    def project_checker(self):
        for project in self.plc:
            lecturer = self.plc[project][0]
            # if each of project and lecturer is undersubscribed
            if self.M[lecturer][2] > 0 and self.M[project][1] > 0:
                deleted_students = self.plc[project][3]
                for student in deleted_students:
                    if self.M[student] == set(): # if student is unassigned in M
                        return True
                    # if student is assigned to a project p_j' that is no better than pj
                    project_rank = self.sp[student][2][project][0]
                    for p in self.M[student]:
                        p_rank = self.sp[student][2][p][0]
                        # student prefers p_j to p_j' or is indifferent between them
                        if project_rank <= p_rank:
                            return True
           
        return False
    
    
    def run(self):
        
        if __name__ == '__main__':
            self.outer_repeat()
            self.check_stability()
        
            # print('student check :::>', self.student_checker())
            # print('project check :::>', self.project_checker())
            # print('lecturer check :::>', self.lecturer_checker())
            # print('blocking pair check :::>', self.blocking_pair)
            # for student in self.sp:
            #     print(student, ':>', self.M[student])
            # for project in self.plc:
            #     print(project, ':>', self.M[project], self.plc[project])
            # for lecturer in self.lp:
            #     print(lecturer, ':>', self.M[lecturer])
            
            if self.student_checker() or self.lecturer_checker() or self.project_checker():
                self.found_susm = 'N'
            
            elif self.blocking_pair is True:
                self.found_susm = 'U'
                
            else:
                self.found_susm = 'Y'
                for student in self.sp:
                    if self.M[student] != set():
                        self.su_M[student] = self.M[student]
            
            return self.found_susm 
    
    
# for k in range(1,10001):    
#     filename = "rg_instances/instance"+str(k)+".txt"
#     s = SuperPoly(filename)
#     r = s.run()
#     if r !='U':
#         print(str(k) + " " + r )
#     else:
#         print(str(k) + " " + r )
#         break