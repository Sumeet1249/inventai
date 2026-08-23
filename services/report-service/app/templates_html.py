"""
Jinja2 HTML template for engineering report with professional CSS
"""

ENGINEERING_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_title }} - Engineering Report</title>
    <style>
        @page {
            size: A4;
            margin: 1cm;
            @bottom-center { content: "Page " counter(page) " of " counter(pages); }
            @bottom-right { content: "{{ timestamp|default('') }}"; }
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #1a1a1a;
            background: white;
        }
        
        .page-break { page-break-after: always; }
        
        /* ═════════════════════════ COVER PAGE ═════════════════════════ */
        .cover-page {
            page-break-after: always;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 60px 40px;
            position: relative;
        }
        
        .cover-header {
            text-align: center;
        }
        
        .cover-logo {
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 20px;
            letter-spacing: -2px;
        }
        
        .cover-title {
            font-size: 42px;
            font-weight: 700;
            margin: 40px 0;
            line-height: 1.2;
        }
        
        .cover-subtitle {
            font-size: 18px;
            opacity: 0.8;
            margin-bottom: 20px;
        }
        
        .cover-footer {
            text-align: center;
        }
        
        .cover-badges {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .badge {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 10pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .badge.confidential {
            background: rgba(220, 38, 38, 0.2);
            border-color: rgba(220, 38, 38, 0.5);
        }
        
        .confidential-banner {
            text-align: center;
            font-size: 28px;
            font-weight: 900;
            color: #dc2626;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin: 40px 0;
            border-top: 2px solid rgba(255,255,255,0.3);
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding: 20px 0;
        }
        
        .cover-meta {
            margin-top: 60px;
            opacity: 0.7;
            font-size: 10pt;
        }
        
        .cover-meta p { margin: 8px 0; }
        
        /* ═════════════════════════ SECTION HEADERS ═════════════════════════ */
        .section-header {
            page-break-before: always;
            margin-top: 40px;
            margin-bottom: 30px;
            border-bottom: 3px solid #0f172a;
            padding-bottom: 15px;
        }
        
        .section-number {
            display: inline-block;
            background: #0f172a;
            color: white;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            border-radius: 4px;
            font-weight: 700;
            margin-right: 15px;
        }
        
        .section-title {
            display: inline-block;
            font-size: 24pt;
            font-weight: 700;
            color: #0f172a;
            vertical-align: middle;
        }
        
        h2 {
            font-size: 18pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 20px;
            margin-bottom: 12px;
        }
        
        h3 {
            font-size: 14pt;
            font-weight: 700;
            color: #1e293b;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        
        h4 {
            font-size: 12pt;
            font-weight: 700;
            color: #334155;
            margin-top: 12px;
            margin-bottom: 8px;
        }
        
        /* ═════════════════════════ CONTENT BLOCKS ═════════════════════════ */
        .content-block {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8fafc;
            border-left: 4px solid #3b82f6;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }
        
        .metric-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 4px;
        }
        
        .metric-label {
            font-size: 9pt;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
        }
        
        /* ═════════════════════════ TABLES ═════════════════════════ */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }
        
        thead {
            background: #f8fafc;
            border-top: 2px solid #0f172a;
            border-bottom: 2px solid #0f172a;
        }
        
        th {
            padding: 12px;
            text-align: left;
            font-weight: 700;
            color: #0f172a;
            font-size: 9pt;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        tbody tr:nth-child(even) {
            background: #f8fafc;
        }
        
        tbody tr:hover {
            background: #f1f5f9;
        }
        
        /* ═════════════════════════ IMAGES ═════════════════════════ */
        .image-container {
            margin: 20px 0;
            text-align: center;
        }
        
        .image-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }
        
        .image-caption {
            font-size: 9pt;
            color: #64748b;
            margin-top: 8px;
            font-style: italic;
        }
        
        /* ═════════════════════════ STATUS BADGES ═════════════════════════ */
        .status-pass {
            display: inline-block;
            background: #dcfce7;
            color: #15803d;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 9pt;
        }
        
        .status-fail {
            display: inline-block;
            background: #fee2e2;
            color: #b91c1c;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 9pt;
        }
        
        .status-warning {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 9pt;
        }
        
        .status-info {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 9pt;
        }
        
        /* ═════════════════════════ CLAIMS/LIST ═════════════════════════ */
        ul, ol {
            margin: 10px 0 10px 20px;
        }
        
        li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        
        /* ═════════════════════════ FOOTER ═════════════════════════ */
        .document-footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 9pt;
            color: #64748b;
            text-align: center;
        }
        
        .footer-text {
            margin: 5px 0;
        }
        
        .footer-hash {
            font-family: 'Courier New', monospace;
            font-size: 8pt;
            color: #94a3b8;
            word-break: break-all;
        }
        
        /* ═════════════════════════ HIGHLIGHTS ═════════════════════════ */
        .highlight-box {
            background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        
        .highlight-title {
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
        }
        
        /* ═════════════════════════ PROGRESS BARS ═════════════════════════ */
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        }
    </style>
</head>
<body>
    <!-- ═════════════════════════ COVER PAGE ═════════════════════════ -->
    <div class="cover-page">
        <div class="cover-header">
            <div class="cover-logo">{{ company_name }}</div>
            <div class="cover-subtitle">Engineering Platform</div>
        </div>
        
        <div>
            <div class="cover-title">{{ project_title }}</div>
            <div class="cover-subtitle">{{ project_subtitle|default('Autonomous Multi-Agent Engineering Package') }}</div>
            
            <div class="cover-badges">
                <div class="badge confidential">{{ confidentiality_level }}</div>
                <div class="badge">{{ timestamp|default('') }}</div>
            </div>
            
            <div class="confidential-banner">CONFIDENTIAL & PROPRIETARY</div>
            
            <div class="cover-meta">
                <p><strong>Project ID:</strong> {{ project_id }}</p>
                <p><strong>Author:</strong> {{ author }}</p>
                <p><strong>Generated:</strong> {{ timestamp|default('N/A') }}</p>
            </div>
        </div>
        
        <div class="cover-footer">
            <p style="opacity: 0.6; margin: 0;">Generated by InventAI Autonomous Engineering Platform</p>
        </div>
    </div>
    
    <!-- ═════════════════════════ SECTION 1: EXECUTIVE SUMMARY ═════════════════════════ -->
    <div class="section-header">
        <span class="section-number">1</span>
        <span class="section-title">Executive Summary & System Specifications</span>
    </div>
    
    <h2>Project Overview</h2>
    <div class="highlight-box">
        <div class="highlight-title">{{ project_title }}</div>
        <p>{{ executive_summary|default('This comprehensive engineering package documents all aspects of the project design, including intellectual property analysis, physics validation, mechanical design, circuit design, and financial projections.') }}</p>
    </div>
    
    {% if business_output %}
    <h3>Financial Snapshot</h3>
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Unit COGS</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.total_cogs_usd) }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Target MSRP</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.target_msrp_usd) }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Gross Margin</div>
            <div class="metric-value">{{ "%.1f"|format(business_output.gross_margin_percent) }}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Profit per Unit</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.target_msrp_usd - business_output.total_cogs_usd) }}</div>
        </div>
    </div>
    {% endif %}
    
    <!-- ═════════════════════════ SECTION 2: PATENT & IP ═════════════════════════ -->
    {% if patent_output %}
    <div class="section-header">
        <span class="section-number">2</span>
        <span class="section-title">Intellectual Property & Freedom to Operate</span>
    </div>
    
    <h2>Patent Analysis & FTO Status</h2>
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Novelty Score</div>
            <div class="metric-value">{{ "%.1f"|format(patent_output.novelty_score) }}/100</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">FTO Status</div>
            <div class="metric-value">
                {% if patent_output.fto_status == 'CLEARED' %}
                    <span class="status-pass">CLEARED</span>
                {% elif patent_output.fto_status == 'BLOCKED' %}
                    <span class="status-fail">BLOCKED</span>
                {% else %}
                    <span class="status-warning">REVIEW NEEDED</span>
                {% endif %}
            </div>
        </div>
    </div>
    
    <h3>White Space Analysis</h3>
    <div class="content-block">
        <p>{{ patent_output.white_space_summary }}</p>
    </div>
    
    {% if patent_output.claims_draft %}
    <h3>Draft Patent Claims</h3>
    <ol>
        {% for claim in patent_output.claims_draft %}
        <li><strong>Claim {{ loop.index }}:</strong> {{ claim }}</li>
        {% endfor %}
    </ol>
    {% endif %}
    {% endif %}
    
    <!-- ═════════════════════════ SECTION 3: PHYSICS & VALIDATION ═════════════════════════ -->
    {% if physics_output %}
    <div class="section-header">
        <span class="section-number">3</span>
        <span class="section-title">Physics & Structural Analysis</span>
    </div>
    
    <h2>PINN Stress Analysis & Validation</h2>
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Validation Status</div>
            <div class="metric-value">
                {% if physics_output.validation_status == 'PASS' %}
                    <span class="status-pass">PASS</span>
                {% else %}
                    <span class="status-fail">FAIL</span>
                {% endif %}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Safety Factor</div>
            <div class="metric-value">{{ "%.2f"|format(physics_output.safety_factor) }}x</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Max Stress</div>
            <div class="metric-value">{{ "%.1f"|format(physics_output.max_stress_mpa) }} MPa</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Yield Strength</div>
            <div class="metric-value">{{ "%.1f"|format(physics_output.yield_strength_mpa) }} MPa</div>
        </div>
    </div>
    
    {% if physics_output.heatmap_image_url %}
    <h3>Stress Distribution Heatmap</h3>
    <div class="image-container">
        <img src="{{ physics_output.heatmap_image_url }}" alt="Stress Heatmap" style="max-width: 100%; max-height: 400px;">
        <div class="image-caption">Figure 3.1: FEA Stress Distribution (PINN Validated)</div>
    </div>
    {% endif %}
    
    <h3>Analysis Summary</h3>
    <div class="content-block">
        <p>{{ physics_output.simulation_summary }}</p>
    </div>
    {% endif %}
    
    <!-- ═════════════════════════ SECTION 4: MECHANICAL CAD ═════════════════════════ -->
    {% if cad_output %}
    <div class="section-header">
        <span class="section-number">4</span>
        <span class="section-title">Mechanical Design & CAD Blueprint</span>
    </div>
    
    <h2>3D Assembly & Component Layout</h2>
    
    {% if cad_output.render_image_url %}
    <div class="image-container">
        <img src="{{ cad_output.render_image_url }}" alt="CAD Assembly" style="max-width: 100%; max-height: 450px;">
        <div class="image-caption">Figure 4.1: 3D CAD Assembly Render ({{ cad_output.format }} Format)</div>
    </div>
    {% endif %}
    
    <h3>Specifications</h3>
    <div class="content-block">
        <p><strong>Format:</strong> {{ cad_output.format }}</p>
        <p><strong>Dimensions:</strong> {{ cad_output.dimensions }}</p>
    </div>
    
    <h3>Assembly Description</h3>
    <div class="content-block">
        <p>{{ cad_output.assembly_summary }}</p>
    </div>
    {% endif %}
    
    <!-- ═════════════════════════ SECTION 5: CIRCUIT & PCB ═════════════════════════ -->
    {% if pcb_output %}
    <div class="section-header">
        <span class="section-number">5</span>
        <span class="section-title">Embedded Electronics & PCB Design</span>
    </div>
    
    <h2>Circuit Design & PCB Layout</h2>
    
    <h3>Board Specifications</h3>
    <div class="content-block">
        <p>{{ pcb_output.board_specs }}</p>
    </div>
    
    {% if pcb_output.layout_image_url %}
    <div class="image-container">
        <img src="{{ pcb_output.layout_image_url }}" alt="PCB Layout" style="max-width: 100%; max-height: 400px;">
        <div class="image-caption">Figure 5.1: PCB Layout & Component Placement</div>
    </div>
    {% endif %}
    
    <h3>SPICE Validation</h3>
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Simulation Status</div>
            <div class="metric-value">
                {% if pcb_output.spice_status == 'PASS' %}
                    <span class="status-pass">PASS</span>
                {% else %}
                    <span class="status-fail">FAIL</span>
                {% endif %}
            </div>
        </div>
    </div>
    
    <h3>Schematic Summary</h3>
    <div class="content-block">
        <p>{{ pcb_output.schematic_summary }}</p>
    </div>
    {% endif %}
    
    <!-- ═════════════════════════ SECTION 6: BOM & FINANCIALS ═════════════════════════ -->
    {% if business_output %}
    <div class="section-header">
        <span class="section-number">6</span>
        <span class="section-title">Bill of Materials & Financial Pro-Forma</span>
    </div>
    
    <h2>Bill of Materials (BOM)</h2>
    
    {% if business_output.bom_table %}
    <table>
        <thead>
            <tr>
                <th>Item #</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit Cost</th>
                <th>Total Cost</th>
                {% if business_output.bom_table[0].supplier %}<th>Supplier</th>{% endif %}
                {% if business_output.bom_table[0].lead_time_days %}<th>Lead Time</th>{% endif %}
            </tr>
        </thead>
        <tbody>
            {% set total_cost = 0 %}
            {% for item in business_output.bom_table %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.item }}</td>
                <td style="text-align: right;">{{ item.qty }}</td>
                <td style="text-align: right; font-family: 'Courier New', monospace;">${{ "%.2f"|format(item.cost) }}</td>
                <td style="text-align: right; font-family: 'Courier New', monospace; font-weight: 700;">${{ "%.2f"|format(item.cost * item.qty) }}</td>
                {% if business_output.bom_table[0].supplier %}<td>{{ item.supplier|default('N/A') }}</td>{% endif %}
                {% if business_output.bom_table[0].lead_time_days %}<td>{{ item.lead_time_days|default('N/A') }} days</td>{% endif %}
            </tr>
            {% set total_cost = total_cost + (item.cost * item.qty) %}
            {% endfor %}
            <tr style="background: #f8fafc; font-weight: 700;">
                <td colspan="4" style="text-align: right;">TOTAL COGS:</td>
                <td style="text-align: right; font-family: 'Courier New', monospace; font-weight: 700; border-top: 2px solid #0f172a;">${{ "%.2f"|format(total_cost) }}</td>
                {% if business_output.bom_table[0].supplier %}<td></td>{% endif %}
                {% if business_output.bom_table[0].lead_time_days %}<td></td>{% endif %}
            </tr>
        </tbody>
    </table>
    {% endif %}
    
    <h2 style="margin-top: 30px;">Financial Analysis</h2>
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Unit COGS</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.total_cogs_usd) }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Target MSRP</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.target_msrp_usd) }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Unit Profit</div>
            <div class="metric-value">${{ "%.2f"|format(business_output.target_msrp_usd - business_output.total_cogs_usd) }}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Gross Margin</div>
            <div class="metric-value">{{ "%.1f"|format(business_output.gross_margin_percent) }}%</div>
        </div>
    </div>
    
    <h3>Financial Summary</h3>
    <div class="content-block">
        <p>{{ business_output.financial_summary }}</p>
    </div>
    {% endif %}
    
    <!-- ═════════════════════════ FOOTER ═════════════════════════ -->
    <div class="document-footer">
        <div class="footer-text">{{ confidentiality_level }} & PROPRIETARY — Do Not Distribute</div>
        <div class="footer-text">Generated by InventAI Autonomous Engineering Platform</div>
        <div class="footer-text">Project ID: {{ project_id }} | {{ timestamp|default('N/A') }}</div>
        <div class="footer-hash">Document Hash: {{ doc_hash|default('auto-generated') }}</div>
    </div>
</body>
</html>
"""
