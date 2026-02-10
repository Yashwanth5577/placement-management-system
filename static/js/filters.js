function applyFilters() {
    const btech = document.querySelector("#btechFilter").value;
    const branch = document.querySelector("#branchFilter").value;
    const gender = document.querySelector("#genderFilter").value;
    const zeroBacklogs = document.querySelector("#zeroBacklogs").checked ? 1 : "";

    let url = "/students?";
    if (btech) url += `btech_min=${btech}&`;
    if (branch) url += `branch=${branch}&`;
    if (gender) url += `gender=${gender}&`;
    if (zeroBacklogs) url += `zero_backlogs=1&`;

    window.location.href = url;

    const backlog = document.querySelector('input[name="max_backlogs"]:checked');
if (backlog) {
    params.append("max_backlogs", backlog.value);
}

}
