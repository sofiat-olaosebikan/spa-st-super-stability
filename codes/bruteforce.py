#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 23:20:17 2019

@author: sofiat
"""

from readinputSPAST import READSPAST


class SUSMBruteForce:
    def __init__(self, filename):

        self.filename = filename
        r = READSPAST()
        r.read_file(self.filename)

        self.students = r.students # no of students
        self.projects = r.projects # no of projects
        self.lecturers = r.lecturers # no of lecturers

        self.sp = r.sp
        self.sp_copy = r.sp_copy
        self.sp_no_tie = r.sp_no_tie
        self.sp_no_tie_deletions = r.sp_no_tie_deletions
        self.plc = r.plc
        self.lp = r.lp
        self.lp_rank = r.lp_rank
        self.proj_rank = r.proj_rank
        self.lp_copy = r.lp_copy
        
        self.M = {s:'' for s in self.sp}
        self.project_wstcounter = {'p' + str(i): [0, []] for i in range(1, len(self.plc)+1)}
        self.lecturer_wstcounter = {'l' + str(i): [0, []] for i in range(1, len(self.lp)+1)}  
        
        self.blocking_pair = False
        self.found_susm = 'N'
    
    # =======================================================================    
    # blocking pair types
    # =======================================================================    
    def blockingpair_1bi(self, student, project, lecturer):
        #  project and lecturer are both under-subscribed
        if self.plc[project][1] > 0 and self.lp[lecturer][0] > 0:
            return True
        return False
    
    def blockingpair_1bii(self, student, project, lecturer):
        # p_j is undersubscribed, l_k is full and either s_i \in M(l_k)
        # or l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
        if self.plc[project][1] > 0 and self.lp[lecturer][0] == 0:
            proj_in_M = self.M[student]
            if proj_in_M != '' and self.plc[proj_in_M][0] == lecturer: # i.e., s_i \in M(l_k)
                return True
            lec_worst_pointer = self.lecturer_wstcounter[lecturer][0]
            student_rank_Lk = self.lp_rank[lecturer][student]
            if student_rank_Lk <= lec_worst_pointer: # l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
                return True            
        return False
    
    def blockingpair_1biii(self, student, project, lecturer):
        # p_j is full and l_k prefers s_i to the worst student in M(p_j) or is indifferent between them
        if self.plc[project][1] == 0:
            proj_worst_pointer = self.project_wstcounter[project][0]
            student_rank_Lkj = self.proj_rank[project][student]
            if student_rank_Lkj <= proj_worst_pointer: # l_k prefers s_i to the worst student in M(l_k) or is indifferent between them
                return True      
        return False
    
   
    
    # =======================================================================    
    # Is M super stable? Check for blocking pair
    # self.blocking_pair is set to True if blocking pair exists
    # =======================================================================
    def check_stability(self):
        self.blocking_pair = False
        for student in self.sp:
            preferred_projects = []
            if self.M[student] == '': 
                preferred_projects = self.sp_no_tie[student]
            else:
                matched_project = self.M[student]
                rank_matched_project = self.sp_copy[student][2][matched_project][0]
                A_si = self.sp_copy[student][1]
                preferred_projects = [s for tie in A_si[:rank_matched_project+1] for s in tie]                
                preferred_projects.remove(matched_project)
        
            for project in preferred_projects:
                lecturer = self.plc[project][0]
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1bi(student,project, lecturer)
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1bii(student, project, lecturer)                    
                if self.blocking_pair is False:
                    self.blocking_pair = self.blockingpair_1biii(student, project, lecturer)
                    #print(student, project, lecturer, self.blocking_pair)
                if self.blocking_pair:                
                    break
            
            # terminate check_stability() as soon as a blocking pair is found
            if self.blocking_pair:                
                break
            
    def choose(self, i):
        # finds ALL possible matching and returns Y if a super stable matching is found
            
        if i > self.students:
            
            # update the project and lecturer worst counter
            for project in self.plc:
                if self.project_wstcounter[project][1] != []:
                    self.project_wstcounter[project][0] = max(self.project_wstcounter[project][1])
            for lecturer in self.lp:
                if self.lecturer_wstcounter[lecturer][1] != []:
                    self.lecturer_wstcounter[lecturer][0] = max(self.lecturer_wstcounter[lecturer][1])
            
            # find a blocking pair and set self.blocking_pair to True
            self.check_stability()
#            matching = {'s1': 'p2', 's2': 'p1', 's3': 'p2'}
#            if self.M == matching:
#                print(len(self.M), self.blocking_pair)
#                
            
            if self.blocking_pair is False:
                self.found_susm = 'Y'
                #exit()
                
                
                # uncomment the next two lines to print a super stable matching
                #print('A super stable matching is: ')
                #print(self.M)
         
            
        else:
            student = "s"+str(i)
            for project in self.sp_no_tie[student]:
                lecturer = self.plc[project][0]
                if self.plc[project][1] > 0 and self.lp[lecturer][0] > 0:
                    self.M[student] = project
                    # decrement the capacity of project and lecturer
                    self.plc[project][1] -= 1
                    self.lp[lecturer][0] -= 1
                    
                    # append the rank of the student currently assigned to each project and lecturer
                    # amend read file to consider student index
                    student_rank_Lk = self.lp_rank[lecturer][student]
                    student_rank_Lkj = self.proj_rank[project][student]
                    self.project_wstcounter[project][1].append(student_rank_Lkj)
                    self.lecturer_wstcounter[lecturer][1].append(student_rank_Lk)
                    
                    self.choose(i+1)
                    
                    self.M[student] = ''
                    student_rank_Lk = self.lp_rank[lecturer][student]
                    student_rank_Lkj = self.proj_rank[project][student]
                    
                    # remove the student's index from the current assignees of the project and lecturer
                    self.project_wstcounter[project][1].remove(student_rank_Lkj)
                    self.lecturer_wstcounter[lecturer][1].remove(student_rank_Lk)

                    # increment project and lecturer capacity 
                    self.plc[project][1] += 1
                    self.lp[lecturer][0] += 1
            self.choose(i+1)
            
        return self.found_susm
   

#filename = "CT/3/instance1117.txt"
#S = SUSMBruteForce(filename)
#result = S.choose(1)
#print(result)