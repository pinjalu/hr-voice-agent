let mediaRecorder;
let audioChunks = [];
let candidateId = null;
let currentState = null;
let isRecording = false;
let currentQuestionIndex = 0;
let totalQuestions = 12;
let isSpeaking = false;

// Confetti effect for completion
function createConfetti() {
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.top = '-10px';
        confetti.style.opacity = '1';
        confetti.style.borderRadius = '50%';
        confetti.style.zIndex = '9999';
        document.body.appendChild(confetti);

        const fall = confetti.animate([
            { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
            { transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
        ], {
            duration: 3000 + Math.random() * 2000,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        });

        fall.onfinish = () => confetti.remove();
    }
}

// Update progress bar
function updateProgress() {
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    progressContainer.classList.add('active');
    const percentage = (currentQuestionIndex / totalQuestions) * 100;
    progressFill.style.width = percentage + '%';
    progressText.textContent = `Question ${currentQuestionIndex} of ${totalQuestions}`;
}

// Show feedback message
function showFeedback(message, isError = false, duration = 3000) {
    const feedback = document.getElementById('feedback');
    feedback.textContent = message;

    // Add/remove error class based on type
    if (isError) {
        feedback.classList.add('error');
    } else {
        feedback.classList.remove('error');
    }

    feedback.classList.add('show');

    setTimeout(() => {
        feedback.classList.remove('show');
        // Clean up error class after hide if needed, 
        // but it will be set next time anyway
    }, duration);
}

// Animate question change
function animateQuestionChange(newText) {
    const questionEl = document.getElementById('question-text');
    questionEl.style.animation = 'none';
    setTimeout(() => {
        questionEl.textContent = newText;
        questionEl.style.animation = 'fadeInScale 0.5s ease-out';
    }, 50);
}

async function register() {
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();

    // Validation Regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Name validation
    if (!name) {
        showFeedback('⚠️ Please enter your name', true);
        nameInput.focus();
        return;
    }
    if (name.length < 2) {
        showFeedback('⚠️ Name must be at least 2 characters long', true);
        nameInput.focus();
        return;
    }

    // Email validation
    if (!email) {
        showFeedback('⚠️ Please enter your email address', true);
        emailInput.focus();
        return;
    }
    if (!emailRegex.test(email)) {
        showFeedback('⚠️ Please enter a valid email address (e.g., name@example.com)', true);
        emailInput.focus();
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);

    try {
        const resp = await fetch('/register', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        candidateId = data.id;

        // Save name for the thank you screen
        const displayName = document.getElementById('display-name');
        if (displayName) displayName.textContent = name;

        document.getElementById('registration-view').classList.add('hidden');
        document.getElementById('interview-view').classList.remove('hidden');

        // Show ready overlay initially
        document.getElementById('ready-overlay').classList.remove('hidden');

        showFeedback('✅ Registration successful! Please get ready...');
        // startInterview() is now called by beginInterview() via the button
    } catch (error) {
        showFeedback('❌ Registration failed. Please try again.', true);
        console.error(error);
    }
}

function beginInterview() {
    const overlay = document.getElementById('ready-overlay');
    overlay.style.opacity = '0';
    setTimeout(() => {
        overlay.classList.add('hidden');
        startInterview();
    }, 500);
}

async function startInterview() {
    try {
        const resp = await fetch(`/interview/start?candidate_id=${candidateId}`, { method: 'POST' });
        const data = await resp.json();

        currentQuestionIndex = 1;
        updateProgress();
        updateUI(data);
    } catch (error) {
        showFeedback('❌ Failed to start interview. Please refresh.');
        console.error(error);
    }
}

function updateUI(data) {
    if (!data || !data.text) {
        console.error("Invalid data received:", data);
        animateQuestionChange("Error: Could not retrieve question.");
        return;
    }

    animateQuestionChange(data.text);
    currentState = data.state;

    if (data.audio_url) {
        const player = document.getElementById('audio-player');
        player.src = data.audio_url;

        // Disable mic during playback
        setMicStatus(false, "🎧 Agent is speaking...");
        const btn = document.getElementById('mic-button');
        btn.classList.add('disabled');
        btn.onclick = null;
        setAvatarSpeaking(true);

        player.onended = () => {
            setAvatarSpeaking(false);
            onAudioEnded();
        };

        player.play().catch(e => {
            console.warn("Audio playback failed, falling back to Web Speech API", e);
            speakText(data.text);
        });
    } else {
        // Fallback to Web Speech API if server TTS is unavailable
        speakText(data.text);
    }

    if (currentState && currentState.current_state === "CLOSING") {
        const player = document.getElementById('audio-player');
        // Wait for ALL speech to complete (Web Speech OR Audio Player)
        const checkSpeechComplete = setInterval(() => {
            const isAudioPlaying = player && !player.paused && !player.ended;
            const isSynthesizing = window.speechSynthesis.speaking;

            if (!isSpeaking && !isSynthesizing && !isAudioPlaying) {
                clearInterval(checkSpeechComplete);
                createConfetti();
                document.getElementById('interview-view').classList.add('hidden');
                document.getElementById('completion-view').classList.remove('hidden');
            }
        }, 500);
    }
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        isSpeaking = true;

        // Animate avatar as speaking
        setAvatarSpeaking(true);

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.10; // Increased speed (was 0.9)
        utterance.pitch = 1.1; // Slightly higher pitch for brighter tone
        utterance.volume = 1;

        // Try to use a pleasant female voice (prioritize Zira on Windows)
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice =>
            voice.name.includes('Zira') ||           // Windows default female
            voice.name.includes('Google US English') || // Chrome default female-sounding
            voice.name.includes('Female') ||         // Generic identifier
            voice.name.includes('Samantha')          // macOS default female
        );

        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        // Disable mic while speaking
        setMicStatus(false, "🎧 Agent is speaking...");
        const btn = document.getElementById('mic-button');
        btn.classList.add('disabled');
        btn.onclick = null; // Remove click handler temporarily

        utterance.onend = () => {
            isSpeaking = false;
            setAvatarSpeaking(false);
            onAudioEnded();
        };
        window.speechSynthesis.speak(utterance);
    } else {
        console.error("Speech synthesis not supported");
        isSpeaking = false;
        onAudioEnded();
    }
}

function setAvatarSpeaking(speaking) {
    const wrapper = document.querySelector('.video-wrapper');
    const indicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');

    if (speaking) {
        wrapper.classList.add('speaking');
        indicator.classList.add('speaking');
        statusText.textContent = 'Speaking...';
    } else {
        wrapper.classList.remove('speaking');
        indicator.classList.remove('speaking');
        statusText.textContent = 'Listening...';
    }
}

function setMicStatus(active, label) {
    const btn = document.getElementById('mic-button');
    const lbl = document.getElementById('mic-label');
    const waveform = document.getElementById('waveform');

    if (active) {
        btn.classList.remove('inactive');
        btn.classList.remove('disabled');
        // btn.classList.add('recording'); // Only add when actually recording
        waveform.classList.add('active');
    } else {
        btn.classList.add('inactive');
        btn.classList.remove('recording');
        waveform.classList.remove('active');
    }
    lbl.textContent = label;
}

function onAudioEnded() {
    const btn = document.getElementById('mic-button');
    btn.classList.remove('disabled');
    btn.onclick = toggleRecording;
    setMicStatus(true, "🎤 Your turn! Click to speak");
    showFeedback('💬 Click the microphone and share your thoughts!', 5000);
}

async function toggleRecording() {
    const btn = document.getElementById('mic-button');
    if (btn.classList.contains('disabled')) return;

    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudio(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        setMicStatus(true, "🔴 Recording... Click to stop");
        showFeedback('🎙️ Recording started! Speak clearly.');
    } catch (error) {
        showFeedback('❌ Microphone access denied. Please allow microphone access.');
        console.error(error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        setMicStatus(false, "🤖 AI is analyzing & generating...");
        showFeedback('✨ AI is thinking...', 8000);
    }
}

async function sendAudio(blob) {
    const formData = new FormData();
    formData.append('candidate_id', candidateId);
    formData.append('state_json', JSON.stringify(currentState));
    formData.append('audio', blob, 'recording.webm');

    try {
        const resp = await fetch('/interview/next', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();

        if (!data.is_retry) {
            currentQuestionIndex++;
            updateProgress();
        }

        if (data.transcription) {
            showFeedback(`✅ Got it: "${data.transcription.substring(0, 50)}..."`, 3000);
        } else if (data.is_retry) {
            showFeedback('⚠️ I didn\'t catch that. Please repeat.', true);
        }

        setTimeout(() => {
            updateUI(data);
        }, 100);
    } catch (error) {
        showFeedback('❌ Failed to process answer. Please try again.');
        console.error(error);
        setMicStatus(true, "🎤 Click to retry");
    }
}

// Load voices when available
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}

async function sendTextAnswer() {
    const input = document.getElementById('text-answer');
    const text = input.value.trim();

    if (!text) {
        showFeedback('⚠️ Please type an answer first', true);
        return;
    }

    // UI Feedback
    input.value = '';
    setMicStatus(false, "🤖 AI is analyzing & generating...");
    showFeedback('✨ AI is thinking...', 8000);

    const formData = new FormData();
    formData.append('candidate_id', candidateId);
    formData.append('state_json', JSON.stringify(currentState));
    formData.append('text_answer', text); // Send text instead of audio

    try {
        const resp = await fetch('/interview/next', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();

        if (!data.is_retry) {
            currentQuestionIndex++;
            updateProgress();
        }

        if (data.transcription) {
            showFeedback(`✅ Processed: "${data.transcription.substring(0, 50)}..."`, 3000);
        } else if (data.is_retry) {
            showFeedback('⚠️ Input not recognized. Please try again.', true);
        }

        setTimeout(() => {
            updateUI(data);
        }, 100);
    } catch (error) {
        showFeedback('❌ Failed to process text answer. Please try again.');
        console.error(error);
        setMicStatus(true, "🎤 Click to retry");
    }
}

// Add Enter key support for text input
document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-answer');
    if (textInput) {
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendTextAnswer();
            }
        });
    }
});
