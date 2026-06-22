/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";

export class ItParcDashboard extends Component {
    static components = { Layout };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            company: "TECHPARK CI",
            subtitle: "",
            kpis: {
                totalEquipment: 0,
                assignedEquipment: 0,
                activeContracts: 0,
                pendingInterventions: 0,
                activeAlerts: 0,
                maintenanceEquipment: 0,
                highAlerts: 0,
            },
            chartData: [],
            stateData: [],
            recentInterventions: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call("it.dashboard", "get_dashboard_data", []);
            this.state.company = data.company;
            this.state.subtitle = data.subtitle;
            this.state.kpis = data.kpis;
            this.state.chartData = data.chartData;
            this.state.stateData = data.stateData;
            this.state.recentInterventions = data.recentInterventions;
            this.state.loading = false;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }

    navigateToEquipment(domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Équipements",
            res_model: "it.equipment",
            views: [[false, "list"], [false, "kanban"], [false, "form"]],
            domain,
        });
    }

    navigateToContracts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Contrats",
            res_model: "it.contract",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "active"]],
        });
    }

    navigateToInterventions() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Interventions",
            res_model: "it.intervention",
            views: [[false, "list"], [false, "calendar"], [false, "form"]],
            domain: [["state", "in", ["draft", "in_progress"]]],
        });
    }

    navigateToAlerts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Alertes",
            res_model: "it.alerte",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "new"]],
        });
    }
}

ItParcDashboard.template = "it_parc.DashboardTemplate";
registry.category("actions").add("it_parc.dashboard", ItParcDashboard);
