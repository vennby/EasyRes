function deleteBio(bioId) {
    fetch('/delete-bio', {
        method: 'POST',
        body: JSON.stringify({ bioId: bioId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}

function deleteEducation(educationId) {
    fetch('/delete-education', {
        method: 'POST',
        body: JSON.stringify({ educationId: educationId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}

function deleteExperience(experienceId) {
    fetch('/delete-experience', {
        method: 'POST',
        body: JSON.stringify({ experienceId: experienceId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}

function deleteProject(projectId) {
    fetch('/delete-project', {
        method: 'POST',
        body: JSON.stringify({ projectId: projectId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}

function deleteSkill(skillId) {
    fetch('/delete-skill', {
        method: 'POST',
        body: JSON.stringify({ skillId: skillId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}
