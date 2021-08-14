# Wrote by Shengqian ZOU, z5203970 at 11/18/2020

# main function
def WAND_Algo(query_terms, top_k, inverted_index):
    query_index = {}
    for term, docid_score in inverted_index.items():  # select the terms which are need
        if term in query_terms:
            query_index[term] = docid_score
    length_query = len(query_terms)
    score = [0 for i in range(length_query)]
    UB = {}
    candidate_pairs = []
    full_evaluation_count = 0

    def max_score(Ut):  # find the max value in the list(UB)
        a = 0
        for i in Ut:
            a = max(a, i[1])
        return a

    for i in range(length_query):
        score[i] = max_score(query_index[query_terms[i]])
        UB[query_terms[i]] = score[i]  # select the UB for each term
        Ct, Wt = query_index[query_terms[i]][0]
        candidate_pairs.append([query_terms[i], [Ct, Wt]])  # put the first posting in candidates
    threshold = 0  # start at 0
    Answer = []

    def check_null(candidate_pairs):  # check all the keys of candidates have value
        a = 0
        for i in range(len(candidate_pairs)):
            if not candidate_pairs[i][1]:
                a += 1
        return a
    # finding the pivot

    def new_candidates(candidate_pairs):  # delete the null value in candidates
        new_candidate = []
        for i in range(len(candidate_pairs)):
            if candidate_pairs[i][1]:
                new_candidate.append(candidate_pairs[i])
        candidate_pairs = new_candidate
        return candidate_pairs
    while candidate_pairs:
        if check_null(candidate_pairs) > 0:
            candidate_pairs = new_candidates(candidate_pairs)
        if len(candidate_pairs[0][1]):  # sorted the list if the list is not null
            candidate_pairs = sorted(candidate_pairs, key=lambda i: i[1][0])
        score_limit = 0
        pivot = 0
        while pivot < len(candidate_pairs):
            if pivot <= (len(candidate_pairs)-1):
                tmp_s_lim = score_limit + UB[candidate_pairs[pivot][0]]
            if tmp_s_lim > threshold:  # if accumulated UB is greater than threshold, enter the function
                full_evaluation_count, threshold, Answer, candidate_pairs = case(full_evaluation_count,
                                                                                  candidate_pairs, pivot,
                                                                                  query_index, threshold, top_k, Answer)
                if check_null(candidate_pairs) > 0:  # delete the null value in candidates
                    candidate_pairs = new_candidates(candidate_pairs)
                break
            # if can not find the pivot(also the last term is not), update posting and delete null key in candidates
            if pivot == (len(candidate_pairs)-1) and tmp_s_lim <= threshold:
                candidate_pairs = next_posting(candidate_pairs, query_index)
                if check_null(candidate_pairs) > 0:
                    candidate_pairs = new_candidates(candidate_pairs)
                break
            else:
                score_limit = tmp_s_lim
                pivot += 1
    Answer = sorted(Answer, key=lambda i: (-i[0], i[1]))   # sorted the answer before return

    return Answer, full_evaluation_count


def check_candidates(candidate_pairs, pivot):  # check the candidates key if have value
    c = 0
    for i in range(len(candidate_pairs)):
        if candidate_pairs[i][1][0] != candidate_pairs[pivot][1][0]:
            c += 1
    return c


# there have 3 case, all terms equal pivot(case1), some terms equal pivot(case2) and have not term equal pivot(case3).
# so need different update the candidates.
def case(full_evaluation_count, candidate_pairs, pivot, query_index, threshold, top_k, Answer):
    # case 1
    if candidate_pairs[0][1][0] == candidate_pairs[pivot][1][0] and check_candidates(candidate_pairs, pivot) == 0:
        s = 0
        t = 0
        while t < len(candidate_pairs) and candidate_pairs[t][1][0] == candidate_pairs[pivot][1][0]:
            s += candidate_pairs[t][1][1]
            t += 1
        if s > threshold:
            Answer.append((s, candidate_pairs[pivot][1][0]))
            if len(Answer) > top_k:
                Answer = delete_min(Answer)
                threshold = minmum(Answer)

        full_evaluation_count += 1
        candidate_pairs = next_posting(candidate_pairs, query_index)
    # case 2
    elif candidate_pairs[0][1][0] == candidate_pairs[pivot][1][0] and check_candidates(candidate_pairs, pivot) != 0:
        s = 0
        t = 0
        while t < len(candidate_pairs) and candidate_pairs[t][1][0] == candidate_pairs[pivot][1][0]:
            s += candidate_pairs[t][1][1]
            t += 1
        if s > threshold:
            Answer.append((s, candidate_pairs[pivot][1][0]))
            if len(Answer) > top_k:
                Answer = delete_min(Answer)
                threshold = minmum(Answer)
        full_evaluation_count += 1
        candidate_pairs = move_before_pivot(pivot, candidate_pairs, query_index)
    else:  # case 3
        for t in range(pivot):
            candidate_pairs[t] = seek_to_document(t, candidate_pairs, pivot, query_index)
    return full_evaluation_count, threshold, Answer, candidate_pairs


def move_before_pivot(pivot, candidate_pairs, query_index):  # update the posting before the pivot term
    candidate_pivot = candidate_pairs[pivot][1][0]
    for i in range(len(candidate_pairs)):
        if len(query_index[candidate_pairs[i][0]])-1 >= query_index[candidate_pairs[i][0]].index((candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1 and candidate_pairs[i][1][0] == candidate_pivot:
            Ct, Wt = query_index[candidate_pairs[i][0]][query_index[candidate_pairs[i][0]].index((candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1]
            candidate_pairs[i][1] = [Ct, Wt]
        elif len(query_index[candidate_pairs[i][0]])-1 < query_index[candidate_pairs[i][0]].index((candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1 and candidate_pairs[i][1][0] == candidate_pivot:
            candidate_pairs[i][1] = []
    new_candidate = []
    for i in range(len(candidate_pairs)):
        if candidate_pairs[i][1]:
            new_candidate.append(candidate_pairs[i])
    return new_candidate


def next_posting(candidate_pairs, query_index):  # update the all terms in candidates
    for i in range(len(candidate_pairs)):
        if len(query_index[candidate_pairs[i][0]]) - 1 >= query_index[candidate_pairs[i][0]].index((candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1:
            Ct, Wt = query_index[candidate_pairs[i][0]][
                query_index[candidate_pairs[i][0]].index((candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1]
            candidate_pairs[i][1] = [Ct, Wt]
        elif len(query_index[candidate_pairs[i][0]]) - 1 < query_index[candidate_pairs[i][0]].index(
                (candidate_pairs[i][1][0], candidate_pairs[i][1][1])) + 1:
            candidate_pairs[i][1] = []
    return candidate_pairs


def delete_min(Answer):  # delete the min-score in answer
    min_score = 999999
    docid = 999999
    for i in range(len(Answer)):
        if min_score > Answer[i][0]:
            min_score, docid = Answer[i]
        if min_score == Answer[i][0]:
            if docid < Answer[i][1]:
                min_score, docid = Answer[i]
    Answer.remove((min_score, docid))
    return Answer


def minmum(Answer):
    min_score = 99999
    for i in range(len(Answer)):
        min_score = min(min_score, Answer[i][0])
    return min_score


def seek_to_document(t, candidate_pairs, pivot, query_index):
    if len(query_index[candidate_pairs[t][0]]) - 1 >= query_index[candidate_pairs[t][0]].index(
            (candidate_pairs[t][1][0], candidate_pairs[t][1][1])) + 1:
        while candidate_pairs[t][1][0] < candidate_pairs[pivot][1][0]:
            if len(query_index[candidate_pairs[t][0]]) - 1 >= query_index[candidate_pairs[t][0]].index(
                    (candidate_pairs[t][1][0], candidate_pairs[t][1][1])) + 1:
                Ct, Wt = query_index[candidate_pairs[t][0]][
                query_index[candidate_pairs[t][0]].index((candidate_pairs[t][1][0], candidate_pairs[t][1][1])) + 1]
                candidate_pairs[t][1] = [Ct, Wt]
            else:
                candidate_pairs[t][1] = []
                break
    else:
        candidate_pairs[t][1] = []
    return candidate_pairs[t]
