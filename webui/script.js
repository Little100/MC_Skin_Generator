/*
 * This file is part of mcskingenerator.
 * mcskingenerator is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * mcskingenerator is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with mcskingenerator. If not, see <https://www.gnu.org/licenses/>.
 */

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("themeToggle")
    const html = document.documentElement

    let skinViewer = null
    let skinViewerInitialized = false

    const savedTheme = localStorage.getItem("theme")

    if (savedTheme) {
        html.className = savedTheme === "dark" ? "dark-theme" : "light-theme"
        themeToggle.classList.toggle("dark", savedTheme === "dark")
    } else {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
        html.className = prefersDark ? "dark-theme" : "light-theme"
        themeToggle.classList.toggle("dark", prefersDark)
        localStorage.setItem("theme", prefersDark ? "dark" : "light")
    }

    themeToggle.addEventListener("click", () => {
        const isDark = html.className === "dark-theme"
        html.className = isDark ? "light-theme" : "dark-theme"
        themeToggle.classList.toggle("dark", !isDark)
        localStorage.setItem("theme", isDark ? "light" : "dark")

        if (skinViewer) {
            skinViewer.updateTheme(!isDark)
        }
    })

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem("theme")) {
            const prefersDark = e.matches
            html.className = prefersDark ? "dark-theme" : "light-theme"
            themeToggle.classList.toggle("dark", prefersDark)

            if (skinViewer) {
                skinViewer.updateTheme(prefersDark)
            }
        }
    })

    const dropArea = document.getElementById("dropArea")
    const fileInput = document.getElementById("fileInput")
    const uploadBtn = document.getElementById("uploadBtn")
    const originalPreview = document.getElementById("originalPreview")
    const skinPreview = document.getElementById("skinPreview")
    const convertBtn = document.getElementById("convertBtn")
    const downloadBtn = document.getElementById("downloadBtn")
    const sizeOptions = document.querySelectorAll('input[name="skinSize"]')
    const historyList = document.getElementById("historyList")
    const loadMoreHistoryBtn = document.getElementById("loadMoreHistoryBtn")

    const poseStanding = document.getElementById("poseStanding")
    const poseWalking = document.getElementById("poseWalking")
    const poseRunning = document.getElementById("poseRunning")
    const viewFront = document.getElementById("viewFront")
    const viewBack = document.getElementById("viewBack")
    const viewLeft = document.getElementById("viewLeft")
    const viewRight = document.getElementById("viewRight")

    let uploadedImage = null
    let convertedSkin = null
    let selectedSize = "64"
    let historyOffset = 0
    const historyLimit = 5
    let isLoadingHistory = false
    let hasMoreHistory = true

    uploadBtn.addEventListener("click", () => fileInput.click())

    fileInput.addEventListener("change", handleFileSelect)

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault()
        dropArea.classList.add("drag-over")
    })

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("drag-over")
    })

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault()
        dropArea.classList.remove("drag-over")

        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files)
        }
    })

    dropArea.addEventListener("click", () => fileInput.click())

    sizeOptions.forEach((option) => {
        option.addEventListener("change", (e) => {
            selectedSize = e.target.value
        })
    })

    convertBtn.addEventListener("click", convertImage)

    downloadBtn.addEventListener("click", downloadSkin)

    loadMoreHistoryBtn.addEventListener("click", () => loadHistory())

    poseStanding.addEventListener("click", () => {
        setActiveButton(poseStanding, [poseWalking, poseRunning])
        if (skinViewer) skinViewer.playAnimation("standing")
    })

    poseWalking.addEventListener("click", () => {
        setActiveButton(poseWalking, [poseStanding, poseRunning])
        if (skinViewer) skinViewer.playAnimation("walking")
    })

    poseRunning.addEventListener("click", () => {
        setActiveButton(poseRunning, [poseStanding, poseWalking])
        if (skinViewer) skinViewer.playAnimation("running")
    })

    viewFront.addEventListener("click", () => {
        setActiveButton(viewFront, [viewBack, viewLeft, viewRight])
        if (skinViewer) skinViewer.setView("front")
    })

    viewBack.addEventListener("click", () => {
        setActiveButton(viewBack, [viewFront, viewLeft, viewRight])
        if (skinViewer) skinViewer.setView("back")
    })

    viewLeft.addEventListener("click", () => {
        setActiveButton(viewLeft, [viewFront, viewBack, viewRight])
        if (skinViewer) skinViewer.setView("left")
    })

    viewRight.addEventListener("click", () => {
        setActiveButton(viewRight, [viewFront, viewBack, viewLeft])
        if (skinViewer) skinViewer.setView("right")
    })

    function setActiveButton(activeBtn, inactiveBtns) {
        activeBtn.classList.add("active")
        inactiveBtns.forEach((btn) => btn.classList.remove("active"))
    }

    function handleFileSelect(e) {
        if (e.target.files.length) {
            handleFiles(e.target.files)
        }
    }

    function handleFiles(files) {
        const file = files[0]

        if (!file.type.match("image.*")) {
            alert("请选择图片文件！")
            return
        }

        const reader = new FileReader()

        reader.onload = (e) => {
            uploadedImage = e.target.result
            displayOriginalImage(uploadedImage)

            convertBtn.disabled = false

            resetSkinPreview()
        }

        reader.readAsDataURL(file)
    }

    function displayOriginalImage(imageSrc) {
        originalPreview.innerHTML = ""

        const img = document.createElement("img")
        img.src = imageSrc
        img.alt = "上传的图片"
        originalPreview.appendChild(img)
    }

    function resetSkinPreview() {
        skinPreview.innerHTML = `
        <div class="skin-model">
          <div class="skin-placeholder">
            <p>皮肤预览将在这里显示</p>
          </div>
        </div>
      `

        downloadBtn.disabled = true
        convertedSkin = null

        document.getElementById("skinViewer3D").innerHTML = `
        <div class="skin-viewer-placeholder">
          <p>转换皮肤后将在此处显示 3D 预览</p>
        </div>
      `
    }

    function convertImage() {
        skinPreview.innerHTML = ""
        skinPreview.classList.add("loading")

        fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: uploadedImage,
                size: selectedSize,
                options: {}
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                skinPreview.classList.remove("loading")

                displayConvertedSkin(data.skin)

                downloadBtn.disabled = false

                convertedSkin = data.skin

                initSkinViewer(data.skin)

                loadHistory(true)
            } else {
                throw new Error(data.message || '转换失败')
            }
        })
        .catch((error) => {
            console.error("转换失败:", error)
            skinPreview.classList.remove("loading")
            skinPreview.innerHTML = `
              <div class="skin-model">
                <div class="skin-placeholder">
                  <p>转换失败，请重试</p>
                </div>
              </div>
            `
        })
    }

    function displayConvertedSkin(skinData) {
        skinPreview.innerHTML = ""

        const img = document.createElement("img")
        img.src = skinData
        img.alt = "转换后的皮肤"
        img.style.imageRendering = "pixelated"
        skinPreview.appendChild(img)
    }

    function downloadSkin() {
        if (!convertedSkin) return

        const link = document.createElement("a")
        link.href = convertedSkin
        link.download = `minecraft-skin-${selectedSize}x${selectedSize}.png`

        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    function initSkinViewer(skinData) {
        try {
            if (!skinViewerInitialized) {
                if (typeof MinecraftSkinViewer !== "function") {
                    throw new Error("MinecraftSkinViewer 类未定义")
                }

                skinViewer = new MinecraftSkinViewer("skinViewer3D")
                skinViewerInitialized = true
            }

            const image = new Image()
            image.onload = function () {
                skinViewer.loadSkin(this)

                skinViewer.playAnimation("standing")
                skinViewer.setView("front")

                const isDark = html.className === "dark-theme"
                skinViewer.updateTheme(isDark)
            }
            image.src = skinData
        } catch (error) {
            console.error("初始化 3D 预览失败:", error)
            document.getElementById("skinViewer3D").innerHTML = `
          <div class="skin-viewer-placeholder">
            <p>3D 预览初始化失败: ${error.message}</p>
          </div>
        `
        }
    }

    async function loadHistory(clearExisting = false) {
        if (isLoadingHistory || !hasMoreHistory) return

        isLoadingHistory = true
        if (clearExisting) {
            historyList.innerHTML = '<p class="loading-history">正在加载历史记录...</p>'
            historyOffset = 0
            hasMoreHistory = true
            loadMoreHistoryBtn.style.display = 'none'
        } else {
            loadMoreHistoryBtn.textContent = '加载中...'
            loadMoreHistoryBtn.disabled = true
        }

        try {
            const response = await fetch(`/api/history?limit=${historyLimit}&offset=${historyOffset}`)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
            const data = await response.json()

            if (data.success) {
                displayHistory(data.history, clearExisting)
                historyOffset += data.history.length
                hasMoreHistory = historyOffset < data.total
                loadMoreHistoryBtn.style.display = hasMoreHistory ? 'block' : 'none'
            } else {
                console.error("获取历史记录失败:", data.message)
                if (clearExisting) {
                    historyList.innerHTML = '<p class="no-history">无法加载历史记录</p>'
                }
                loadMoreHistoryBtn.style.display = 'none'
            }
        } catch (error) {
            console.error("加载历史记录时出错:", error)
            if (clearExisting) {
                historyList.innerHTML = '<p class="no-history">加载历史记录时出错</p>'
            }
            loadMoreHistoryBtn.style.display = 'none'
        } finally {
            isLoadingHistory = false
            loadMoreHistoryBtn.textContent = '加载更多'
            loadMoreHistoryBtn.disabled = false
        }
    }

    function displayHistory(historyData, clearExisting) {
        if (clearExisting) {
            historyList.innerHTML = ''
        }

        const initialMsg = historyList.querySelector('.no-history, .loading-history')
        if (initialMsg) {
            initialMsg.remove()
        }

        if (historyData.length === 0 && clearExisting) {
            historyList.innerHTML = '<p class="no-history">暂无历史记录</p>'
            return
        }

        historyData.forEach(item => {
            const historyItem = document.createElement('div')
            historyItem.classList.add('history-item')

            const originalImg = document.createElement('img')
            originalImg.src = item.originalImage
            originalImg.alt = '原始图片缩略图'
            originalImg.classList.add('history-thumbnail')

            const skinImg = document.createElement('img')
            skinImg.src = item.convertedSkin
            skinImg.alt = '转换后的皮肤'
            skinImg.classList.add('history-skin')
            skinImg.style.imageRendering = 'pixelated'

            const infoDiv = document.createElement('div')
            infoDiv.classList.add('history-info')
            infoDiv.innerHTML = `
                <p>尺寸: ${item.size}x${item.size}</p>
                <p>时间: ${new Date(item.createdAt).toLocaleString()}</p>
            `

            const actionsDiv = document.createElement('div')
            actionsDiv.classList.add('history-actions')
            const downloadLink = document.createElement('a')
            downloadLink.href = item.convertedSkin
            downloadLink.download = `minecraft-skin-${item.size}x${item.size}-${item.id.substring(0, 8)}.png`
            downloadLink.textContent = '下载'
            downloadLink.classList.add('history-download-btn')
            actionsDiv.appendChild(downloadLink)

            historyItem.appendChild(originalImg)
            historyItem.appendChild(skinImg)
            historyItem.appendChild(infoDiv)
            historyItem.appendChild(actionsDiv)

            historyList.appendChild(historyItem)
        })
    }

    loadHistory(true)
})
