const WORLD_ID = '109';
const POSTCODE = '3168';

class HexagonalVisualization {
    constructor() {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.breadcrumb = document.getElementById('breadcrumb');
        this.actionButtons = document.getElementById('action-buttons');
        
        this.hexSize = 60;
        this.offsetX = 0;
        this.offsetY = 0;
        this.scale = 1;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        this.currentView = 'world';
        this.selectedDistrict = null;
        this.selectedHousehold = null;
        this.currentDate = null;
        this.availableDates = [];
        
        this.worldData = null;
        this.districtData = null;
        this.householdData = null;
        this.timelineData = null;
        
        this.hexagons = [];
        
        this.init();
    }
    
    async init() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.onMouseUp());
        this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
        this.canvas.addEventListener('click', (e) => this.onClick(e));
        
        await this.loadWorldData();
        this.updateBreadcrumb();
        this.render();
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.render();
    }
    
    async loadWorldData() {
        try {
            const response = await fetch(`/worlds/${WORLD_ID}/world.json`);
            this.worldData = await response.json();
        } catch (error) {
            console.error('Failed to load world data:', error);
        }
    }
    
    async loadDistrictData() {
        try {
            const response = await fetch(`/worlds/${WORLD_ID}/${POSTCODE}/district.json`);
            this.districtData = await response.json();
        } catch (error) {
            console.error('Failed to load district data:', error);
        }
    }
    
    async loadHouseholdData(houseId) {
        try {
            const response = await fetch(`/worlds/${WORLD_ID}/${POSTCODE}/${houseId}/household.json`);
            this.householdData = await response.json();
            
            await this.scanAvailableDates(houseId);
        } catch (error) {
            console.error('Failed to load household data:', error);
        }
    }
    
    async scanAvailableDates(houseId) {
        try {
            const response = await fetch(`/api/dates?world_id=${WORLD_ID}&postcode=${POSTCODE}&house_id=${houseId}`);
            if (response.ok) {
                this.availableDates = await response.json();
                if (this.availableDates.length > 0) {
                    this.currentDate = this.availableDates[this.availableDates.length - 1];
                }
                console.log('Available dates:', this.availableDates);
                console.log('Current date:', this.currentDate);
            } else {
                console.error('Failed to fetch dates from API');
                this.availableDates = [];
            }
        } catch (error) {
            console.error('Error scanning dates:', error);
            this.availableDates = [];
        }
    }
    
    async loadTimelineData(houseId, date) {
        try {
            const members = this.householdData.members;
            this.timelineData = {};
            
            for (const member of members) {
                const memberName = encodeURIComponent(member.name);
                const response = await fetch(`/outputs/${WORLD_ID}/${POSTCODE}/${houseId}/${date}/04_第四层_批量用电决策_${memberName}.json`);
                if (response.ok) {
                    this.timelineData[member.name] = await response.json();
                }
            }
        } catch (error) {
            console.error('Failed to load timeline data:', error);
        }
    }
    
    updateBreadcrumb() {
        let html = '';
        
        if (this.currentView === 'world') {
            html = '<span class="breadcrumb-item">🌍 世界</span>';
        } else if (this.currentView === 'district') {
            html = `
                <span class="breadcrumb-item" onclick="app.goToWorld()">🌍 世界</span>
                <span class="breadcrumb-separator">›</span>
                <span class="breadcrumb-item">🏘️ ${POSTCODE} Clayton</span>
            `;
        } else if (this.currentView === 'timeline') {
            html = `
                <span class="breadcrumb-item" onclick="app.goToWorld()">🌍 世界</span>
                <span class="breadcrumb-separator">›</span>
                <span class="breadcrumb-item" onclick="app.goToDistrict()">🏘️ ${POSTCODE} Clayton</span>
                <span class="breadcrumb-separator">›</span>
                <span class="breadcrumb-item">🏠 ${this.selectedHousehold}</span>
            `;
        }
        
        this.breadcrumb.innerHTML = html;
        this.updateActionButtons();
    }
    
    updateActionButtons() {
        let html = '';
        
        if (this.currentView === 'timeline') {
            html = `
                <div class="control-panel" style="display: flex; gap: 10px;">
                    <button class="btn btn-secondary" id="backBtn">← 返回</button>
                    <button class="btn" id="refreshBtn">🔄 刷新</button>
                    <button class="btn" id="prevDay">← 前一天</button>
                    <span class="date-display" id="currentDateDisplay">${this.formatDate(this.currentDate)}</span>
                    <button class="btn" id="nextDay">后一天 →</button>
                </div>
            `;
        } else {
            html = '<button class="btn" id="refreshBtn">🔄 刷新</button>';
        }
        
        this.actionButtons.innerHTML = html;
        
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refresh();
        }
        
        if (this.currentView === 'timeline') {
            document.getElementById('backBtn').onclick = () => this.goToDistrict();
            document.getElementById('prevDay').onclick = () => this.changeDate(-1);
            document.getElementById('nextDay').onclick = () => this.changeDate(1);
        }
    }
    
    async refresh() {
        if (this.currentView === 'world') {
            await this.loadWorldData();
            this.render();
        } else if (this.currentView === 'district') {
            await this.loadDistrictData();
            await this.loadWorldData();
            this.render();
        } else if (this.currentView === 'timeline') {
            await this.scanAvailableDates(this.selectedHousehold);
            await this.loadTimelineData(this.selectedHousehold, this.currentDate);
            this.renderAllMembersTimeline();
            this.updateActionButtons();
        }
    }
    
    async goToWorld() {
        this.currentView = 'world';
        this.selectedDistrict = null;
        this.selectedHousehold = null;
        
        const container = document.getElementById('canvas-container');
        container.classList.remove('timeline-view');
        if (!document.getElementById('canvas')) {
            container.innerHTML = '<canvas id="canvas"></canvas>';
            this.canvas = document.getElementById('canvas');
            this.ctx = this.canvas.getContext('2d');
            this.resizeCanvas();
        }
        
        this.resetView();
        this.updateBreadcrumb();
        this.render();
    }
    
    async goToDistrict() {
        this.currentView = 'district';
        this.selectedHousehold = null;
        
        const container = document.getElementById('canvas-container');
        container.classList.remove('timeline-view');
        if (!document.getElementById('canvas')) {
            container.innerHTML = '<canvas id="canvas"></canvas>';
            this.canvas = document.getElementById('canvas');
            this.ctx = this.canvas.getContext('2d');
            this.resizeCanvas();
        }
        
        await this.loadDistrictData();
        this.resetView();
        this.updateBreadcrumb();
        this.render();
    }
    
    async goToHousehold() {
        await this.goToDistrict();
    }
    
    async goToTimeline() {
        this.currentView = 'timeline';
        await this.loadTimelineData(this.selectedHousehold, this.currentDate);
        this.updateBreadcrumb();
        this.renderTimeline();
    }
    
    resetView() {
        this.offsetX = 0;
        this.offsetY = 0;
        this.scale = 1;
    }
    
    hexToPixel(q, r) {
        const x = this.hexSize * (3/2 * q);
        const y = this.hexSize * (Math.sqrt(3)/2 * q + Math.sqrt(3) * r);
        return { x, y };
    }
    
    drawHexagon(x, y, size, color, text, subtext = '') {
        const centerX = this.canvas.width / 2 + (x + this.offsetX) * this.scale;
        const centerY = this.canvas.height / 2 + (y + this.offsetY) * this.scale;
        const scaledSize = size * this.scale;
        
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = Math.PI / 3 * i;
            const hx = centerX + scaledSize * Math.cos(angle);
            const hy = centerY + scaledSize * Math.sin(angle);
            if (i === 0) {
                this.ctx.moveTo(hx, hy);
            } else {
                this.ctx.lineTo(hx, hy);
            }
        }
        this.ctx.closePath();
        
        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        
        this.ctx.fillStyle = '#fff';
        this.ctx.font = `bold ${14 * this.scale}px sans-serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(text, centerX, centerY - (subtext ? 8 * this.scale : 0));
        
        if (subtext) {
            this.ctx.font = `${11 * this.scale}px sans-serif`;
            this.ctx.fillText(subtext, centerX, centerY + 12 * this.scale);
        }
        
        return { centerX, centerY, scaledSize };
    }
    
    isPointInHexagon(px, py, hexX, hexY, size) {
        const dx = Math.abs(px - hexX);
        const dy = Math.abs(py - hexY);
        
        if (dx > size * 0.866 || dy > size) return false;
        
        return size * 1.5 - 0.866 * dx - 0.5 * dy >= 0;
    }
    
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.hexagons = [];
        
        if (this.currentView === 'world') {
            this.renderWorld();
        } else if (this.currentView === 'district') {
            this.renderDistrict();
        } else if (this.currentView === 'household') {
            this.renderHousehold();
        }
    }
    
    renderWorld() {
        if (!this.worldData) return;
        
        const hex = this.drawHexagon(0, 0, this.hexSize, '#667eea', POSTCODE, 'Clayton');
        this.hexagons.push({
            ...hex,
            type: 'district',
            data: { postcode: POSTCODE }
        });
    }
    
    renderDistrict() {
        if (!this.worldData) return;
        
        const households = this.worldData.households;
        const radius = 2;
        let index = 0;
        
        for (let q = -radius; q <= radius; q++) {
            for (let r = Math.max(-radius, -q - radius); r <= Math.min(radius, -q + radius); r++) {
                if (index >= households.length) break;
                
                const household = households[index];
                const pos = this.hexToPixel(q, r);
                
                const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
                const color = colors[index % colors.length];
                
                const hex = this.drawHexagon(
                    pos.x, 
                    pos.y, 
                    this.hexSize, 
                    color, 
                    household.house_id.replace('house_', ''),
                    household.type
                );
                
                this.hexagons.push({
                    ...hex,
                    type: 'household',
                    data: household
                });
                
                index++;
            }
        }
    }
    
    renderHousehold() {
        if (!this.householdData) return;
        
        const members = this.householdData.members;
        const radius = 1;
        let index = 0;
        
        for (let q = -radius; q <= radius; q++) {
            for (let r = Math.max(-radius, -q - radius); r <= Math.min(radius, -q + radius); r++) {
                if (index >= members.length) break;
                
                const member = members[index];
                const pos = this.hexToPixel(q, r);
                
                const color = member.gender === '男' ? '#4facfe' : '#f093fb';
                
                const hex = this.drawHexagon(
                    pos.x, 
                    pos.y, 
                    this.hexSize, 
                    color, 
                    member.name,
                    member.occupation
                );
                
                this.hexagons.push({
                    ...hex,
                    type: 'member',
                    data: member
                });
                
                index++;
            }
        }
    }
    
    renderTimeline() {
        const container = document.getElementById('canvas-container');
        container.innerHTML = '';
        container.classList.add('timeline-view');
        
        const timelineDiv = document.createElement('div');
        timelineDiv.className = 'timeline-container';
        
        const header = document.createElement('div');
        header.className = 'timeline-header';
        header.innerHTML = `<h2>🏠 ${this.householdData.home.name}</h2>`;
        timelineDiv.appendChild(header);
        
        const timelineContent = document.createElement('div');
        timelineContent.id = 'timeline-content';
        timelineDiv.appendChild(timelineContent);
        
        container.appendChild(timelineDiv);
        
        this.renderAllMembersTimeline();
        this.updateActionButtons();
    }
    
    renderAllMembersTimeline() {
        const content = document.getElementById('timeline-content');
        const members = Object.keys(this.timelineData);
        
        let html = '';
        
        members.forEach((memberName) => {
            const data = this.timelineData[memberName];
            const member = this.householdData.members.find(m => m.name === memberName);
            const color = member.gender === '男' ? '#4facfe' : '#f093fb';
            
            html += `
                <div class="member-section">
                    <div class="member-header">
                        <div class="member-avatar" style="background: ${color};">
                            ${member.gender === '男' ? '👨' : '👩'}
                        </div>
                        <div class="member-info">
                            <h3>${memberName}</h3>
                            <div class="member-meta">
                                <span>👔 ${member.occupation}</span>
                                <span>🎂 ${member.age}岁</span>
                                <span>⚡ ${data.total_energy_kwh.toFixed(2)} kWh</span>
                            </div>
                        </div>
                    </div>
            `;
            
            data.appliance_decisions.forEach(item => {
                const activeAppliances = item.operations.filter(op => op.action === 'use' || op.action === 'charge_home');
                
                html += `
                    <div class="timeline-item">
                        <div class="timeline-time">${item.time}</div>
                        <div class="timeline-content">
                            <div class="timeline-location">📍 ${item.location}</div>
                            <div class="timeline-activity">${item.activity}</div>
                            ${activeAppliances.length > 0 ? `
                                <div class="timeline-appliances">
                                    ${activeAppliances.map(op => {
                                        const name = op.unique_id.split('_').pop();
                                        const className = op.action === 'use' ? 'use' : 'charge';
                                        return `<span class="appliance-tag ${className}">${name}</span>`;
                                    }).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        });
        
        const totalEnergy = members.reduce((sum, name) => sum + this.timelineData[name].total_energy_kwh, 0);
        html += `
            <div class="energy-summary total">
                <h3>📊 家庭总用电量</h3>
                <div class="energy-value">${totalEnergy.toFixed(2)} kWh</div>
                <div style="margin-top: 10px; opacity: 0.9; font-size: 14px;">
                    ${this.formatDate(this.currentDate)}
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }
    
    formatDate(dateStr) {
        const year = dateStr.substring(0, 4);
        const month = dateStr.substring(4, 6);
        const day = dateStr.substring(6, 8);
        return `${year}年${month}月${day}日`;
    }
    
    async changeDate(delta) {
        const currentIndex = this.availableDates.indexOf(this.currentDate);
        const newIndex = currentIndex + delta;
        
        if (newIndex >= 0 && newIndex < this.availableDates.length) {
            this.currentDate = this.availableDates[newIndex];
            await this.loadTimelineData(this.selectedHousehold, this.currentDate);
            this.renderAllMembersTimeline();
            this.updateActionButtons();
        }
    }
    
    onClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        for (const hex of this.hexagons) {
            if (this.isPointInHexagon(x, y, hex.centerX, hex.centerY, hex.scaledSize)) {
                this.handleHexClick(hex);
                break;
            }
        }
    }
    
    async handleHexClick(hex) {
        if (hex.type === 'district') {
            this.selectedDistrict = hex.data.postcode;
            this.currentView = 'district';
            await this.loadDistrictData();
            this.resetView();
            this.updateBreadcrumb();
            this.render();
        } else if (hex.type === 'household') {
            this.selectedHousehold = hex.data.house_id;
            await this.loadHouseholdData(this.selectedHousehold);
            await this.goToTimeline();
        }
    }
    
    onMouseDown(e) {
        if (this.currentView === 'timeline') return;
        this.isDragging = true;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
    }
    
    onMouseMove(e) {
        if (!this.isDragging || this.currentView === 'timeline') return;
        
        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;
        
        this.offsetX += dx / this.scale;
        this.offsetY += dy / this.scale;
        
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
        
        this.render();
    }
    
    onMouseUp() {
        this.isDragging = false;
    }
    
    onWheel(e) {
        if (this.currentView === 'timeline') return;
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = this.scale * delta;
        
        if (newScale >= 0.5 && newScale <= 3) {
            this.scale = newScale;
            this.render();
        }
    }
}

let app;
window.addEventListener('DOMContentLoaded', () => {
    app = new HexagonalVisualization();
});