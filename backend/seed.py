import uuid
from backend.database import SessionLocal, engine
from backend.models import Property, PropertyZone, SlangDictionary, Base

def seed_database():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Create a default property
        prop_id = uuid.UUID("3d183980-ff6d-4952-b883-7c3852d7e5b6")
        existing_prop = db.query(Property).filter_by(id=prop_id).first()
        if not existing_prop:
            prop = Property(
                id=prop_id,
                name="Central Office Plaza",
                address="8 Finance St, Central, Hong Kong"
            )
            db.add(prop)
            print("Seeded Property: Central Office Plaza")
        else:
            prop = existing_prop
            print("Property already exists")

        # 2. Create a default property zone (matching QR_ZONE_987654)
        zone_id = uuid.UUID("98739861-777c-4bad-a81f-b22e12861642")
        existing_zone = db.query(PropertyZone).filter_by(id=zone_id).first()
        if not existing_zone:
            zone = PropertyZone(
                id=zone_id,
                property_id=prop.id,
                name="Lobby Restroom",
                floor_type="tile",
                square_footage=1500,
                qr_code_token="987654",
                latitude=22.2855,
                longitude=114.1577
            )
            db.add(zone)
            print("Seeded PropertyZone: Lobby Restroom (QR Code: 987654)")
        else:
            print("PropertyZone already exists")

        # 3. Seed Spanish slang mappings
        slang_items = [
            ("pulidora de pisos", "floor buffer / burnisher", "maint_needed"),
            ("poda de jardin", "turf lawn trimming", "service_trigger"),
            ("bano sucio", "restroom sanitation alert", "sanitation_needed"),
            ("manguera rota", "broken pressure washing hose", "equipment_alert"),
            ("quimicos terminados", "chemical supply depletion", "supply_depleted"),
            ("espejo roto", "broken mirror", "equipment_alert")
        ]

        for phrase, canonical, trigger in slang_items:
            existing_slang = db.query(SlangDictionary).filter_by(phrase=phrase).first()
            if not existing_slang:
                slang = SlangDictionary(
                    phrase=phrase,
                    canonical_english=canonical,
                    action_trigger=trigger
                )
                db.add(slang)
                print(f"Seeded Slang Mapping: '{phrase}' -> '{canonical}'")
        
        db.commit()
        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print("Error seeding database:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
