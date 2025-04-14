function deleteSkill(skillId) {
    fetch('/delete-skill', {
        method: 'POST',
        body: JSON.stringify({ skillId: skillId }),
    }).then((_res) => {
        window.location.href = "/profile";
    });
}

function deleteExperience(experienceId) {
    fetch('/delete-experience', {
        method: 'POST',
        body: JSON.stringify({ experienceId: experienceId }),
    }).then((_res) => {
        window.location.href = "/profile";  // Reload the profile page after deletion
    });
}