from sigma.processing.pipeline import ProcessingPipeline

# Map common Sigma field names to normalized ECS-like fields used in this project.
DEFAULT_FIELD_MAPPING = {
    # Process fields
    "Image": "process.name",
    "FileName": "process.name",
    "ProcessName": "process.name",
    "ParentImage": "process.parent.name",
    "CommandLine": "process.command_line",
    "ParentCommandLine": "process.parent.command_line",
    # User fields
    "TargetUserName": "user.name",
    "TargetUser": "user.name",
    "AccountName": "user.name",
    "User": "user.name",
    # IPs
    "SourceIp": "source.ip",
    "SourceIpAddress": "source.ip",
    "DestinationIp": "destination.ip",
    "DstIp": "destination.ip",
    # Network
    "Url": "url.full",
    "Hostname": "host.name",
    # Windows specifics
    "ServiceName": "service.name",
}


def get_default_processing_pipeline() -> ProcessingPipeline:
    """Return a ProcessingPipeline configured with the default field name mapping."""
    pipeline_dict = {
        "transformations": [
            {
                "type": "field_name_mapping",
                "mapping": DEFAULT_FIELD_MAPPING,
            }
        ]
    }
    return ProcessingPipeline.from_dict(pipeline_dict)
