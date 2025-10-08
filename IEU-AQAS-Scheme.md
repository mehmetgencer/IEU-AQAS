---
title: AQAS- Program Outcomes Evaluation
numbersections: true
#$$ sudo apt-get install pandoc groff ghostscript
#$ pandoc --pdf-engine=pdfroff --number-sections --output=IEU-AQAS-scheme.pdf IEU-AQAS-Scheme.md
#$ pandoc --toc --standalone --mathml -f markdown -t html5 IEU-AQAS-Scheme.md -o IEU-AQAS-Scheme.html
---

# From courses to program outcomes

## Program outcomes (PO) definition

Each program, $p$, is defined as a set of program outcomes, $O_p$.

## Course activities to learning outcomes (LO)

Let $C_p$ be the set of core courses in a diploma programme, $p$. For any course, $c \in C_p$, there is a set of learning outcomes, $L_c$.

Each course has a set of assessment activities, $A_c$. Each activity of a course, $a \in A_c$, contributes to one or more of the course learning outcomes. For example, $LOcontrib_{c,a,l}$ is the  contribution of activity $a \in A_c$ to learning outcome $l \in L_c$ for course $c$. These contributions form a preliminarly A-to-LO contribution matrix for the course, $X'_c$ , whose elements are $x'^{c}_{a,l}= LOcontrib_{c,a,l}$ .

For the sake of simplicity the matrix $X'_c$ is a binary matrix, i.e. the values $LOcontrib_{c,a,l}$ can take only values 0 or 1. However, there is also the problem that activities are of  different weightage, $w_{c,a}$, forming a weightage matrix of the course activities, $\mathbf{w_c}$. For example, weight of final exam can be 30% (i.e. 0.3) whereas a homework can be 10%. To account for these differences we use a weighted A-to-LO contribution matrix: $X_c=\mathbf{w_c} X'_c$

Each course also has an ECTS credit value, $ects_c$ which will be used later for the level of contribution.

## From LO to PO

In order to assess achievement of program outcomes, $O_p$, for a course in the program, $c \in C_p$, its learning outcomes will be mapped to program outcomes. For example contribution value of a learning outcome, $l \in L_c$ to a program outcome, $o \in O_p$ is denoted as $POcontrib_{c,l,o}$. These contributions form a LO-to-PO contribution matrix for the course, $Y_c$, whose elements are $y^c_{l,o}=POcontrib_{c,l,o}$.

For the sake of simplicity the matrix $Y_c$ is a binary matrix, i.e. the values $POcontrib_{c,l,o}$ can take only values 0 or 1.

# Evaluation

## Evaluation based on course designs: New scheme (for the future)

Here the aim is to evaluate the level which courses in the curriculum, via their learning outcomes, support the program outcomes.

A first step to compute this would be to compute contribution of a course to programme outcomes as $T^c=Y_c^T X_c$, and collapse the activities level to obtain a vector of PO contributions of a course. Let us denote this resulting vector as $\mathbf{z^c}$ whose elements represent contribution of all activities of the course to each program outcome $o_i$, i.e. $z^c_i=\sum_{j}t_{i,j}$

One can then sum this over all courses in a program's curriculum to find the support for program outcomes: $\sum_{c \in C_p}\mathbf{z^c}$. However, the main problem here is that courses have different ECTS values, different number of learning outcomes and different number of program outcomes each LO contributes to. Thus, values in the total contribution vector of a course to program outcomes, $TotalContrib_c=\sum\mathbf{z^c}$, can be very different across courses and not necessarily proportional to course's ECTS credits. Hence a **normalization** is needed. A straightforward solution is to ensure that sum of contributions of a course is equal to its ECTS credit, by normalizing as:

$$ \mathbf{z^c_{norm}}=\mathbf{z^c} \frac{ects_c}{TotalContrib_c}$$


To find the support of the whole curriculum for each of the program outcomes, one must sum normalized contributions of all courses as follows (please see the practical note in the next section for a tentative, realistic calculation of the following): 

$$\sum_{c \in C_p} \mathbf{z^c_{norm}}$$

## A practical evaluation based on existing information

In IEU system the syllabus declares the $\mathbf{z^c}$ matrix regardless of the activities' contributions. Ideally the declared matrix and matrix computed as a bove should be the same; i.e. in the future we must use the computed contributions matrix, $POcontrib$, instead of directly entering some numbers into the table in the syllabus. For now, however, we must skip the computations and use the declared contributions in the syllabus. Thus, for the rest of this section, assume that $\mathbf{z^c}$ is obtained from syllabus, rather than being derived by following A-to-LO and LO-to-PO contribution levels. 


## Evaluation based on student grades: using existing information

To simplify evaluation, also assume that we only have the overall course grade (over 100) of students, rather than a grade breakdown for all course activities. Let's denote the grade of a student, $s$, who passed a course, $c$, in a diploma program, $p$, ad  $g_{s,c}^p$.  In this scheme averaging the value $g_{s,c}^p \mathbf{z^c_{norm}}$ over all students will give use the achievements of program outcomes based on success of program's students, $S_p$, in that particular course. Summing over all core courses will provide avhievement levels of each program outcomes as a vector:

$$\sum_{c \in C_p}{\overline{g}_{s,c}^p \mathbf{z^c_{norm}}}$$


