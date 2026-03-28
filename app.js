document.addEventListener('DOMContentLoaded', function() {
    // Event Data from external event_data.js
    const events = typeof calendarEvents !== 'undefined' ? calendarEvents : [];

    // Initialize FullCalendar
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        initialDate: '2026-03-01',
        locale: 'ko',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listMonth'
        },
        buttonText: {
            today: '오늘',
            month: '월간',
            week: '주간',
            list: '목록'
        },
        height: '100%',
        events: events,
        eventClick: function(info) {
            info.jsEvent.preventDefault(); // don't let the browser navigate
            showModal(info.event);
        },
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false
        },
        displayEventEnd: true
    });

    calendar.render();

    // Modal Logic
    const modalOverlay = document.getElementById('eventModal');
    const closeModalBtn = document.getElementById('closeModal');
    
    function showModal(event) {
        // Elements
        const titleEl = document.getElementById('modalTitle');
        const dateEl = document.getElementById('modalDate');
        const descEl = document.getElementById('modalDescription');
        const badgeEl = document.getElementById('modalCategory');
        
        const priceEl = document.getElementById('modalPrice');
        const urlWrap = document.querySelector('.modal-link-wrap');
        const urlEl = document.getElementById('modalUrl');

        const props = event.extendedProps;
        
        // Setup data
        titleEl.textContent = event.title;
        
        let dateStr = event.start.toLocaleDateString('ko-KR', {
            year: 'numeric', month: 'long', day: 'numeric', weekday: 'short'
        });
        if (event.end) {
            // Because FullCalendar end dates are exclusive, subtract one day
            let endDate = new Date(event.end);
            endDate.setDate(endDate.getDate() - 1);
            dateStr += ' ~ ' + endDate.toLocaleDateString('ko-KR', {
                year: 'numeric', month: 'long', day: 'numeric', weekday: 'short'
            });
        }
        dateEl.textContent = dateStr;
        descEl.innerHTML = props.description.replace(/\n/g, '<br>');
        
        badgeEl.textContent = props.categoryLabel;
        badgeEl.className = `badge ${props.category}`;
        
        // Handle Price and Link
        if(props.price) {
            priceEl.textContent = props.price;
        } else {
            priceEl.textContent = '정보 없음';
        }
        
        if(props.url) {
            urlWrap.style.display = 'block';
            urlEl.href = props.url;
        } else {
            urlWrap.style.display = 'none';
            urlEl.href = '#';
        }

        // Show
        modalOverlay.classList.remove('hidden');
    }

    function hideModal() {
        modalOverlay.classList.add('hidden');
    }

    closeModalBtn.addEventListener('click', hideModal);
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) hideModal();
    });
    
    // Allow Escape key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape" && !modalOverlay.classList.contains('hidden')) {
            hideModal();
        }
    });

    // To ensure the calendar renders optimally when the window resizes
    window.addEventListener('resize', function() {
        calendar.updateSize();
    });
});
