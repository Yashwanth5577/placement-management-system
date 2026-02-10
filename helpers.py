from sqlalchemy import or_

def apply_student_filters(query, args, Student):
    """
    Apply all filters consistently for both
    students list and download
    """

    percent_filters = args.getlist("percent")
    branch_filters = args.getlist("branch")
    gender_filters = args.getlist("gender")
    zero_backlogs = args.get("zero")

    # B.Tech percentage filters (multi-select)
    if percent_filters:
        query = query.filter(
            or_(*[Student.btech_percentage >= float(p) for p in percent_filters])
        )

    # Branch filter
    if branch_filters:
        query = query.filter(Student.branch.in_(branch_filters))

    # Gender filter
    if gender_filters:
        query = query.filter(Student.gender.in_(gender_filters))

    # Zero backlog filter
    if zero_backlogs:
        query = query.filter(Student.backlogs == 0)

    return query
