// AI Interview Agent - Custom JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new window.bootstrap.Tooltip(tooltipTriggerEl))

  // Initialize popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
  var popoverList = popoverTriggerList.map((popoverTriggerEl) => new window.bootstrap.Popover(popoverTriggerEl))

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Auto-hide alerts after 5 seconds
  setTimeout(() => {
    const alerts = document.querySelectorAll(".alert:not(.alert-permanent)")
    alerts.forEach((alert) => {
      const bsAlert = new window.bootstrap.Alert(alert)
      bsAlert.close()
    })
  }, 5000)

  // Form validation enhancement
  const forms = document.querySelectorAll(".needs-validation")
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  })

  // Character counter for textareas
  const textareas = document.querySelectorAll("textarea[data-max-length]")
  textareas.forEach((textarea) => {
    const maxLength = Number.parseInt(textarea.getAttribute("data-max-length"))
    const counter = document.createElement("div")
    counter.className = "text-muted small text-end mt-1"
    counter.innerHTML = `<span class="current">0</span>/${maxLength} characters`
    textarea.parentNode.appendChild(counter)

    textarea.addEventListener("input", function () {
      const current = this.value.length
      const currentSpan = counter.querySelector(".current")
      currentSpan.textContent = current

      if (current > maxLength * 0.9) {
        counter.classList.add("text-warning")
        counter.classList.remove("text-muted")
      } else {
        counter.classList.add("text-muted")
        counter.classList.remove("text-warning")
      }
    })
  })

  // Progress tracking
  function updateProgress() {
    fetch("/api/progress")
      .then((response) => response.json())
      .then((data) => {
        if (data.progress !== undefined) {
          const progressBars = document.querySelectorAll(".progress-bar[data-auto-update]")
          progressBars.forEach((bar) => {
            bar.style.width = data.progress + "%"
            bar.setAttribute("aria-valuenow", data.progress)
          })
        }
      })
      .catch((error) => console.log("Progress update failed:", error))
  }

  // Update progress every 30 seconds if on interview page
  if (window.location.pathname.includes("/interview")) {
    setInterval(updateProgress, 30000)
  }

  // Keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const activeForm = document.querySelector("form:focus-within")
      if (activeForm) {
        const submitBtn = activeForm.querySelector('button[type="submit"]')
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.click()
        }
      }
    }

    // Escape to clear focused textarea
    if (e.key === "Escape") {
      const activeTextarea = document.activeElement
      if (activeTextarea && activeTextarea.tagName === "TEXTAREA") {
        activeTextarea.value = ""
        activeTextarea.focus()
      }
    }
  })

  // Auto-save functionality for long forms
  const autoSaveForms = document.querySelectorAll("form[data-auto-save]")
  autoSaveForms.forEach((form) => {
    const formId = form.getAttribute("data-auto-save")

    // Load saved data
    const savedData = localStorage.getItem("autosave_" + formId)
    if (savedData) {
      try {
        const data = JSON.parse(savedData)
        Object.keys(data).forEach((key) => {
          const field = form.querySelector(`[name="${key}"]`)
          if (field) {
            field.value = data[key]
          }
        })
      } catch (e) {
        console.log("Failed to load auto-saved data:", e)
      }
    }

    // Save data on input
    form.addEventListener("input", () => {
      const formData = new FormData(form)
      const data = {}
      for (const [key, value] of formData.entries()) {
        data[key] = value
      }
      localStorage.setItem("autosave_" + formId, JSON.stringify(data))
    })

    // Clear saved data on successful submit
    form.addEventListener("submit", () => {
      localStorage.removeItem("autosave_" + formId)
    })
  })

  // Copy to clipboard functionality
  const copyButtons = document.querySelectorAll("[data-copy-target]")
  copyButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const targetSelector = this.getAttribute("data-copy-target")
      const target = document.querySelector(targetSelector)

      if (target) {
        const text = target.textContent || target.value
        navigator.clipboard
          .writeText(text)
          .then(() => {
            // Show success feedback
            const originalText = button.innerHTML
            button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!'
            button.classList.add("btn-success")

            setTimeout(() => {
              button.innerHTML = originalText
              button.classList.remove("btn-success")
            }, 2000)
          })
          .catch((err) => {
            console.error("Failed to copy text: ", err)
          })
      }
    })
  })

  // Lazy loading for images
  const images = document.querySelectorAll("img[data-src]")
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.remove("lazy")
        imageObserver.unobserve(img)
      }
    })
  })

  images.forEach((img) => imageObserver.observe(img))

  // Dark mode toggle (if implemented)
  const darkModeToggle = document.querySelector("#darkModeToggle")
  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode")
      const isDark = document.body.classList.contains("dark-mode")
      localStorage.setItem("darkMode", isDark)
    })

    // Load dark mode preference
    const isDarkMode = localStorage.getItem("darkMode") === "true"
    if (isDarkMode) {
      document.body.classList.add("dark-mode")
    }
  }

  // Enhanced file upload with preview
  const fileInputs = document.querySelectorAll('input[type="file"][data-preview]')
  fileInputs.forEach((input) => {
    input.addEventListener("change", function () {
      const file = this.files[0]
      const previewContainer = document.querySelector(this.getAttribute("data-preview"))

      if (file && previewContainer) {
        const reader = new FileReader()
        reader.onload = (e) => {
          if (file.type.startsWith("image/")) {
            previewContainer.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`
          } else {
            previewContainer.innerHTML = `
                            <div class="d-flex align-items-center">
                                <i class="fas fa-file fa-2x me-3"></i>
                                <div>
                                    <div class="fw-bold">${file.name}</div>
                                    <div class="text-muted small">${formatFileSize(file.size)}</div>
                                </div>
                            </div>
                        `
          }
        }
        reader.readAsDataURL(file)
      }
    })
  })

  // Utility function to format file size
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  // Initialize any custom components
  initializeCustomComponents()
})

// ==========================================
// VOICE RECORDING FUNCTIONALITY REMOVED
// ==========================================
// Voice recording is now handled in interview.html template
// to avoid JavaScript conflicts and variable redeclaration
// This ensures better separation of concerns and prevents
// the "mediaRecorder already declared" and function
// definition errors seen in the browser console.

// Custom component initialization
function initializeCustomComponents() {
  // Initialize any custom dropdowns, modals, etc.
  console.log("Custom components initialized")
  
  // Log if we're on the interview page
  if (window.location.pathname.includes("/interview")) {
    console.log("Interview page detected - audio functionality handled by page-specific scripts")
  }
}

// Global utility functions
window.AIInterviewApp = {
  showNotification: (message, type = "info") => {
    const alertDiv = document.createElement("div")
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`
    alertDiv.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;"
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `
    document.body.appendChild(alertDiv)

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove()
      }
    }, 5000)
  },

  confirmAction: (message, callback) => {
    if (confirm(message)) {
      callback()
    }
  },

  formatTime: (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`
  },

  // Utility to check if user is on interview page
  isInterviewPage: () => {
    return window.location.pathname.includes("/interview")
  },

  // Utility to show loading state
  showLoading: (element, text = "Loading...") => {
    if (element) {
      const originalHTML = element.innerHTML
      element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`
      element.disabled = true
      
      return () => {
        element.innerHTML = originalHTML
        element.disabled = false
      }
    }
  },

  // Utility to validate form fields
  validateForm: (form) => {
    const requiredFields = form.querySelectorAll("[required]")
    let isValid = true
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        field.classList.add("is-invalid")
        isValid = false
      } else {
        field.classList.remove("is-invalid")
        field.classList.add("is-valid")
      }
    })
    
    return isValid
  }
}