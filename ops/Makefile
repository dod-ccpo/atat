.PHONY: delete-deployment reset-phase1 phase1 phase2

delete-deployment:
	# This test is CRITICAL, because if this executes with an empty string, it'll delete every resource group.
	test -n "$(DEPLOYMENT)"  # $$DEPLOYMENT
	./dangerously_delete_resource_groups.sh $(DEPLOYMENT)


reset-phase1:
	rm -rf ../terraform/providers/bootstrap/.terraform ../terraform/providers/bootstrap/terraform.tfstate* ../terraform/providers/bootstrap/versions.override.tf phase1/service_principal.json

reset-phase2:
	rm -rf ../terraform/providers/application_env/.terraform

# These are currently not working
# phase1: reset-phase1
# 	test -n "$(DEPLOYMENT)"  # $$DEPLOYMENT
# 	test -n "$(RHEL_USERNAME)"  # $$RHEL_USERNAME
# 	test -n "$(RHEL_PASSWORD)"  # $$RHEL_PASSWORD
# 	cd phase1; ./run.sh $(DEPLOYMENT) $(RHEL_USERNAME) $(RHEL_PASSWORD)

# phase2: reset-phase2
# 	cd phase2; python provisioner.py | tee output.log
