function removeListItemById(listId, itemId, isSkill = false) {
  const list = document.getElementById(listId);
  if (!list) return;
  const item = document.getElementById(itemId);
  if (item) {
    item.classList.add("fade-out");
    setTimeout(() => {
      // Remove the item from the DOM after fade-out
      if (isSkill) {
        // For skills, check if this was the last skill in its group
        const groupListItem = item.closest("li.list-group-item");
        if (groupListItem) {
          item.remove();
          // Check if there are any remaining skills in this group
          const remainingSkills = groupListItem.querySelectorAll(
            "ul.list-inline > li"
          );
          if (remainingSkills.length === 0) {
            groupListItem.classList.add("fade-out");
            setTimeout(() => {
              groupListItem.remove();
            }, 400);
          }
        }
      } else {
        item.remove();
      }
    }, 400);
  }
}

function deleteBio(bioId) {
  fetch("/delete-bio", {
    method: "POST",
    body: JSON.stringify({ bioId: bioId }),
  }).then((_res) => {
    removeListItemById("bio", "bio-" + bioId);
  });
}

function deleteEducation(educationId) {
  fetch("/delete-education", {
    method: "POST",
    body: JSON.stringify({ educationId: educationId }),
  }).then((_res) => {
    removeListItemById("education", "education-" + educationId);
  });
}

function deleteExperience(experienceId) {
  fetch("/delete-experience", {
    method: "POST",
    body: JSON.stringify({ experienceId: experienceId }),
  }).then((_res) => {
    removeListItemById("experience", "experience-" + experienceId);
  });
}

function deleteProject(projectId) {
  fetch("/delete-project", {
    method: "POST",
    body: JSON.stringify({ projectId: projectId }),
  }).then((_res) => {
    removeListItemById("project", "project-" + projectId);
  });
}

function deleteSkill(skillId) {
  fetch("/delete-skill", {
    method: "POST",
    body: JSON.stringify({ skillId: skillId }),
  }).then((_res) => {
    removeListItemById("skill", "skill-" + skillId, true);
  });
}

// Generic AJAX form handler
function handleProfileForm(formId, listId) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    fetch(window.location.pathname, {
      method: "POST",
      body: formData,
    })
      .then((res) => res.text())
      .then((html) => {
        // Parse the returned HTML and update the relevant list
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newList = doc.getElementById(listId);
        if (newList) {
          document.getElementById(listId).innerHTML = newList.innerHTML;
        }
        form.reset();
      });
  });
}

// Attach handlers for all forms
handleProfileForm("bio-form", "bio");
handleProfileForm("education-form", "education");
handleProfileForm("experience-form", "experience");
handleProfileForm("project-form", "project");
handleProfileForm("skill-form", "skill");

// Dynamic resume search on homepage
function setupResumeSearch() {
  const searchInput = document.querySelector(
    '.search-bar input[name="search"]'
  );
  if (!searchInput) return;
  searchInput.addEventListener("input", function () {
    const query = searchInput.value.trim().toLowerCase();
    const cards = document.querySelectorAll(".card.h-100");
    let anyVisible = false;
    cards.forEach((card) => {
      const title = card
        .querySelector(".card-title")
        .textContent.trim()
        .toLowerCase();
      if (query === "" || title.includes(query)) {
        card.parentElement.style.display = "";
        anyVisible = true;
      } else {
        card.parentElement.style.display = "none";
      }
    });
    // Show/hide the 'No resumes found' message
    const noResumesMsg = document.querySelector(
      ".col-12.text-center.text-muted"
    );
    if (noResumesMsg) {
      noResumesMsg.style.display = anyVisible ? "none" : "";
    }
  });
}

document.addEventListener("DOMContentLoaded", setupResumeSearch);
